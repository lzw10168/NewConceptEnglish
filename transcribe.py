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
    model = whisper.load_model("base")
    
    # 转录音频
    print("Transcribing audio...")
    result = model.transcribe(
        audio_path,
        language="en",
        task="transcribe"
    )
    
    # 准备输出内容
    if format == "json":
        # JSON 格式，适合播放器歌词显示
        # import json
        print("Translating segments...")

        lyrics_data = {
            "lyrics": [
                {
                    "startTime": segment["start"] * 1000,  # 转换为毫秒
                    "endTime": segment["end"] * 1000,      # 转换为毫秒
                    "text": segment["text"].strip(),
                    "translation": translate_text(segment["text"].strip())
                }
                for segment in result["segments"]
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
    # 替换为你的音频文件路径
    audio_file = "./audio/nce1/095.mp3"
    
    # 生成输出文件名（使用当前时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存为纯文本格式
    # txt_output = f"transcription_{timestamp}.txt"
    # print("\nGenerating text format with timestamps...")
    # txt_result = transcribe_audio(audio_file, txt_output, format="txt")
    # print("\nText format result:")
    # print(txt_result)
    
    # # 保存为 SRT 格式
    # srt_output = f"transcription_{timestamp}.srt"
    # print("\nGenerating SRT format...")
    # srt_result = transcribe_audio(audio_file, srt_output, format="srt")
    # print("\nSRT format saved to:", srt_output)

    # 保存为 JSON 格式
    json_output = f"transcription_{timestamp}.json"
    print("\nGenerating JSON format...")
    json_result = transcribe_audio(audio_file, json_output, format="json")
    print("\nJSON format saved to:", json_output)
    # translate_text("Hello, world!")
