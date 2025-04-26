import whisper
import os
from datetime import datetime
from openai import OpenAI, DefaultHttpxClient
import httpx
 
client = OpenAI(
    api_key = "sk-gbiQ0jHq0zqtp6qRP1tk9KfIfWRA1Kfcv3mXxjeQ8goX4eI0",
    base_url = "https://api.moonshot.cn/v1",
)
 

def translate_text(text):
    """将英文文本翻译为中文"""
    try:
        completion = client.chat.completions.create(
            model = "moonshot-v1-8k",
            messages = [
                {"role": "system", "content": "You are a translator. Translate the following English text to Chinese."},
                {"role": "user", "content": text}
            ],
            temperature = 0.3,
        )
        
        print(completion.choices[0].message.content)

        # print(response.output_text)
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Translation error: {e}")
        return "Translation failed"

def format_timestamp(seconds):
    """将秒数转换为 HH:MM:SS,mmm 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def transcribe_audio(audio_path, output_path=None, format="txt"):
    """
    将音频文件转换为带时间戳的文本
    
    Args:
        audio_path: 音频文件路径
        output_path: 输出文件路径（可选）
        format: 输出格式，支持 "txt"、"srt" 或 "json"（可选）
    
    Returns:
        转录的文本内容
    """
    # 加载模型
    print("Loading model...")
    model = whisper.load_model("medium")
    
    # 转录音频
    print("Transcribing audio...")
    result = model.transcribe(
        audio_path,
        language="en",
        task="transcribe"
    )
    
    # 准备输出内容
    if format == "json":
        print("Translating segments...")
        
        lyrics_data = {
            "lyrics": [
                {
                    "startTime": segment["start"] * 1000,
                    "endTime": segment["end"] * 1000,
                    "text": segment["text"].strip(),
                    "translation": translate_text(segment["text"].strip()),
                    # 添加一个标记来指示是否是问题开始
                    "isHeader": "then answer the question" in (result["segments"][i-1]["text"].lower() if i > 0 else "") if i < len(result["segments"]) else False
                }
                for i, segment in enumerate(result["segments"])
            ]
        }
        import json
        output_text = json.dumps(lyrics_data, ensure_ascii=False, indent=2)
    
    elif format == "txt":
        # 纯文本格式，每行包含时间戳和文本
        output_lines = []
        for segment in result["segments"]:
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
            output_lines.append(f"[{start_time} --> {end_time}] {text}")
        output_text = "\n".join(output_lines)
    
    elif format == "srt":
        # SRT 字幕格式
        output_lines = []
        for i, segment in enumerate(result["segments"], 1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
            output_lines.extend([
                str(i),
                f"{start_time} --> {end_time}",
                text,
                ""  # 空行分隔不同的字幕块
            ])
        output_text = "\n".join(output_lines)
    
    # 如果指定了输出路径，将文本保存到文件
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Transcription saved to: {output_path}")
    
    return output_text

# 使用示例
if __name__ == "__main__":
    # 指定输入和输出目录
    input_dir = "./audio/nce3"
    output_dir = "./output/nce3"  # 新建一个输出目录
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有 mp3 文件
    audio_files = [f for f in os.listdir(input_dir) if f.endswith('.mp3')]
    
    # 按文件名排序
    audio_files.sort()
    
    # 处理每个音频文件
    for audio_file in audio_files:
        input_path = os.path.join(input_dir, audio_file)
        # 使用原文件名，但改为.json后缀
        output_filename = os.path.splitext(audio_file)[0] + '.json'
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"\nProcessing: {audio_file}")
        print(f"Generating JSON format...")
        json_result = transcribe_audio(input_path, output_path, format="json")
        print(f"JSON format saved to: {output_path}")
    # translate_text("Hello, world!")
