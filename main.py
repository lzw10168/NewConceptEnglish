import whisper
import os
import re
from datetime import timedelta
from difflib import SequenceMatcher

# 加载模型
model = whisper.load_model("medium")  # 可以根据需要选择模型大小

# 设置路径
audio_dir = "./NCE2/audio"
text_dir = "./NCE2/en"
output_dir = "./NCE2/lrc"

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

    # 提取词级别的时间戳
    word_timestamps = []
    for segment in result["segments"]:
        if "words" in segment:
            for word in segment["words"]:
                # 检查并适应不同的数据结构格式
                if isinstance(word, dict):
                    word_text = word.get("word", word.get("text", "")).lower().strip()
                    word_start = word.get("start", 0)
                    word_end = word.get("end", 0)
                else:
                    # 如果word是元组或列表形式
                    word_text = str(word[0]).lower().strip() if len(word) > 0 else ""
                    word_start = float(word[1]) if len(word) > 1 else 0
                    word_end = float(word[2]) if len(word) > 2 else 0

                if word_text:  # 只添加非空的词
                    word_timestamps.append({
                        "text": word_text,
                        "start": word_start,
                        "end": word_end
                    })

    # 创建原始文本的数组
    text_segments = []
    for line in original_lines:
        text_segments.append({"text": line, "start": None})

    # 对每一行文本，通过查找第一个显著词的时间戳来确定开始时间
    for i, segment in enumerate(text_segments):
        text = segment["text"].lower()
        words = text.split()
        
        # 跳过常见的无意义词
        skip_words = {"a", "the", "in", "on", "at", "and", "or", "but", "to", "of"}
        
        # 找到第一个有意义的词
        significant_words = [w for w in words if len(w) > 2 and w not in skip_words]
        
        if i == 0:  # 第一行（标题）
            segment["start"] = 0.0
            continue
            
        if significant_words:
            target_word = significant_words[0]
            # 在word_timestamps中查找这个词
            best_match_time = None
            best_match_score = 0
            
            # 设置搜索窗口
            start_idx = 0
            if i > 0 and text_segments[i-1]["start"] is not None:
                # 从上一行时间戳后开始搜索
                for idx, w in enumerate(word_timestamps):
                    if w["start"] >= text_segments[i-1]["start"]:
                        start_idx = idx
                        break
            
            # 在窗口内搜索最佳匹配
            for word_info in word_timestamps[start_idx:]:
                word = word_info["text"].lower().strip()
                # 使用更灵活的匹配方式
                if (target_word in word or word in target_word) and len(word) > 2:
                    similarity = SequenceMatcher(None, target_word, word).ratio()
                    if similarity > best_match_score:
                        best_match_score = similarity
                        best_match_time = word_info["start"]
                        
                # 如果找到很好的匹配就停止搜索
                if best_match_score > 0.8:
                    break
            
            if best_match_time is not None:
                segment["start"] = best_match_time

    # 处理未匹配的行
    last_time = 0
    for i, segment in enumerate(text_segments):
        if segment["start"] is None:
            if i > 0 and text_segments[i-1]["start"] is not None:
                # 估算间隔时间（基于文本长度）
                prev_time = text_segments[i-1]["start"]
                text_length = len(segment["text"].split())
                estimated_duration = max(2.0, min(text_length * 0.3, 4.0))
                segment["start"] = prev_time + estimated_duration
            else:
                segment["start"] = last_time + 3.0
        
        # 确保时间戳严格递增
        if i > 0:
            segment["start"] = max(segment["start"], text_segments[i-1]["start"] + 0.5)
        
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
# process_lesson("001")

# 批量处理所有课程


def process_all_lessons():
    # 获取所有mp3文件并排序
    files = [f for f in os.listdir(audio_dir) if f.endswith(".mp3")]
    files.sort()  # 按文件名字母顺序排序
    
    for filename in files:
        lesson_number = filename.split('.')[0]
        process_lesson(lesson_number)

# 如需批量处理，取消下面的注释
process_all_lessons()
