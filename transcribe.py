import whisper
import os
from datetime import datetime
from openai import OpenAI, DefaultHttpxClient
import httpx
import soundfile as sf
import argparse
import json

client = OpenAI(
    api_key = "sk-gbiQ0jHq0zqtp6qRP1tk9KfIfWRA1Kfcv3mXxjeQ8goX4eI0",
    base_url = "https://api.moonshot.cn/v1",
)

def read_reference_text(lesson_num):
    """从课程JSON文件中读取参考文本"""
    try:
        ref_path = f"./data/nce1/course-1-{lesson_num}.json"
        with open(ref_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 提取对话文本
            dialogue = data.get("dialogueText", {}).get("notes", [])
            # 合并所有对话行
            return " ".join([line.split("\t")[0] for line in dialogue if "\t" in line])
    except Exception as e:
        print(f"Warning: Could not read reference text: {e}")
        return None

def translate_text(text):
    """将英文文本翻译为中文"""
    try:
        completion = client.chat.completions.create(
            model = "moonshot-v1-8k",
            messages = [
                {"role": "system", "content": "You are a translator. Translate the following English text to Chinese. 这是新概念三课程的句子, 请你充分理解上下文, 对每个句子做出合理的翻译. "},
                {"role": "user", "content": text}
            ],
            temperature = 0.3,
        )
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

def clean_segments(segments, max_duration):
    """清理重复的段落并确保不超过音频实际长度"""
    cleaned = []
    seen_texts = set()
    
    for segment in segments:
        text = segment["text"].strip()
        # 如果时间超过最大时长或文本重复，就跳过
        if segment["end"] >= max_duration- 2.5 or text in seen_texts:
            continue
        
        cleaned.append(segment)
        seen_texts.add(text)
    
    return cleaned

def transcribe_audio(audio_path, output_path=None, format="txt"):
    """将音频文件转换为带时间戳的双语文本"""
    print("Loading model...")
    model = whisper.load_model("large-v3-turbo")
    
    # 获取课程编号
    lesson_num = os.path.basename(audio_path)[:3]
    
    # 读取参考文本
    reference_text = read_reference_text(lesson_num)
    
    print("Transcribing audio...")
    result = model.transcribe(
        audio_path,
        language="en",
        task="transcribe",
        initial_prompt=reference_text if reference_text else None
    )
    
    # 获取音频实际长度
    audio_info = sf.info(audio_path)
    max_duration = audio_info.duration
    print('max_duration: ', max_duration)
    
    # 清理识别结果
    result["segments"] = clean_segments(result["segments"], max_duration)
    
    # 如果有参考文本，使用参考文本替换识别文本
    if reference_text:
        ref_lines = [line.strip() for line in reference_text.split(".") if line.strip()]
        for i, segment in enumerate(result["segments"]):
            if i < len(ref_lines):
                segment["text"] = ref_lines[i].strip()
    
    # 准备整个文本用于翻译
    full_text = "\n".join([segment["text"].strip() for segment in result["segments"]])
    
    # 一次性翻译整个文本
    print("Translating full text...")
    full_translation = translate_text(full_text)
    
    # 将翻译结果按段落拆分
    translations = full_translation.split("\n")
    
    if format == "json":
        print("Generating bilingual JSON...")
        segments = result["segments"]
        lyrics_data = {
            "title": os.path.splitext(os.path.basename(audio_path))[0],
            "lyrics": [
                {
                    "startTime": segment["start"] * 1000,
                    "endTime": segment["end"] * 1000,
                    "text": segment["text"].strip(),
                    "translation": translations[i] if i < len(translations) else "",
                    "isHeader": " Listen to" in segment["text"]
                }
                for i, segment in enumerate(segments)
            ]
        }
        output_text = json.dumps(lyrics_data, ensure_ascii=False, indent=2)
    
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Bilingual transcription saved to: {output_path}")
    
    return output_text

# 使用示例
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio files from specified lesson number')
    parser.add_argument('start_lesson', type=str, help='Starting lesson number (e.g. 001)')
    parser.add_argument('end_lesson', type=str, nargs='?', help='Ending lesson number (optional, e.g. 003)')
    args = parser.parse_args()

    input_dir = "./audio/nce1"
    output_dir = "./output/nce1"
    
    os.makedirs(output_dir, exist_ok=True)
    
    audio_files = [f for f in os.listdir(input_dir) if f.endswith('.mp3')]
    audio_files.sort()
    
    filtered_files = []
    for file in audio_files:
        lesson_num = file[:3]
        if args.end_lesson:
            if args.start_lesson <= lesson_num <= args.end_lesson:
                filtered_files.append(file)
        else:
            if args.start_lesson <= lesson_num:
                filtered_files.append(file)
    
    for audio_file in filtered_files:
        input_path = os.path.join(input_dir, audio_file)
        output_filename = os.path.splitext(audio_file)[0] + '.json'
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"\nProcessing: {audio_file}")
        print(f"Generating JSON format...")
        json_result = transcribe_audio(input_path, output_path, format="json")
        print(f"JSON format saved to: {output_path}")
