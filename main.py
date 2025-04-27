import whisper
import os
import re
from datetime import timedelta

# 加载模型
model = whisper.load_model("medium")  # 可以根据需要选择模型大小

# 设置路径
audio_dir = "C:/Users/zhiwei.li/Downloads/NewConceptEnglish/NCE2/audio"
text_dir = "C:/Users/zhiwei.li/Downloads/NewConceptEnglish/NCE2/en"
output_dir = "C:/Users/zhiwei.li/Downloads/NewConceptEnglish/NCE2/lrc"

os.makedirs(output_dir, exist_ok=True)


def format_timestamp(seconds):
    """将秒数格式化为LRC时间戳格式 [MM:SS.mmm]"""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"[{minutes:02d}:{seconds:06.3f}]".replace(".", ":")[:11]


def process_lesson(lesson_number):
    # 格式化课程编号为三位数字
    lesson_id = f"{int(lesson_number):03d}"
    audio_file = os.path.join(audio_dir, f"{lesson_id}.mp3")
    text_file = os.path.join(text_dir, f"{lesson_id}.txt")

    if not os.path.exists(audio_file) or not os.path.exists(text_file):
        print(f"文件不存在: {audio_file} 或 {text_file}")
        return

    # 读取原始文本
    with open(text_file, "r", encoding="utf-8") as f:
        original_lines = [line.strip()
                          for line in f.readlines() if line.strip()]

    # 使用Whisper转录音频
    print(f"处理课程 {lesson_id}...")
    result = model.transcribe(
        audio_file,
        task="transcribe",
        language="en",
        word_timestamps=True
    )

    # 使用模糊匹配算法将Whisper的识别结果与原始文本对齐
    whisper_segments = []
    for segment in result["segments"]:
        start_time = segment["start"]
        whisper_segments.append({
            "text": segment["text"],
            "start": start_time
        })

    # 创建原始文本的数组（保留所有行，包括标题和问题）
    text_segments = []
    for line in original_lines:
        text_segments.append({"text": line, "start": None})

    # 基于文本相似度匹配Whisper段落和原始文本
    from difflib import SequenceMatcher

    def clean_text(text):
        return re.sub(r'[^\w\s]', '', text.lower())

    # 匹配并分配时间戳
    for i, text_segment in enumerate(text_segments):
        best_match_score = 0
        best_match_time = 0

        text_clean = clean_text(text_segment["text"])
        for whisper_segment in whisper_segments:
            whisper_clean = clean_text(whisper_segment["text"])

            # 使用SequenceMatcher计算相似度
            similarity = SequenceMatcher(
                None, text_clean, whisper_clean).ratio()

            # 如果是课程标题，使用特殊匹配
            if i == 0 and "Lesson" in text_segment["text"]:
                if similarity > 0.3:  # 对标题行降低匹配阈值
                    best_match_time = whisper_segment["start"]
                    break
            elif similarity > best_match_score:
                best_match_score = similarity
                best_match_time = whisper_segment["start"]

        # 如果找到匹配，分配时间戳
        if best_match_score > 0.5 or (i == 0 and "Lesson" in text_segment["text"] and best_match_time > 0):
            text_segment["start"] = best_match_time
        else:
            # 尝试使用相邻段落的时间戳进行插值
            if i > 0 and text_segments[i-1]["start"] is not None:
                # 如果前一个有时间戳，估计当前段落的时间戳
                text_segment["start"] = text_segments[i -
                                                      # 假设每段相差5秒
                                                      1]["start"] + 5.0

    # 处理可能缺失的时间戳（如果有）
    last_time = 0
    for segment in text_segments:
        if segment["start"] is None:
            segment["start"] = last_time + 4.0  # 为缺失的段落估计时间
        else:
            last_time = segment["start"]

    # 生成LRC文件
    output_lrc = os.path.join(output_dir, f"{lesson_id}.lrc")
    with open(output_lrc, "w", encoding="utf-8") as f:
        for segment in text_segments:
            timestamp = format_timestamp(segment["start"])
            f.write(f"{timestamp} {segment['text']}\n")

    print(f"已完成课程 {lesson_id} 的处理，LRC文件保存为: {output_lrc}")

    return output_lrc


# 处理单个课程
process_lesson("001")

# 批量处理所有课程


def process_all_lessons():
    for filename in os.listdir(audio_dir):
        if filename.endswith(".mp3"):
            lesson_number = filename.split('.')[0]
            process_lesson(lesson_number)

# 如需批量处理，取消下面的注释
# process_all_lessons()
