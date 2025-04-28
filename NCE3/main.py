import requests
from bs4 import BeautifulSoup
import os
import re
import time
import json
from openai import OpenAI

# Create directories if they don't exist
os.makedirs('audio', exist_ok=True)
os.makedirs('en', exist_ok=True)
os.makedirs('zh', exist_ok=True)
os.makedirs('words', exist_ok=True)

# Set your OpenAI API key
# You'll need to set this before running
client = OpenAI(
    api_key="sk-QeJTJShZ1gl5oT23MXlE8v5gYSVgfnnN2ZZ2ZLu3cF2ifkTy",
    base_url="https://api.moonshot.cn/v1",
)


def get_lesson_content(lesson_id):
    url = f"https://www.ha85.com/lessons/{lesson_id}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to get lesson {lesson_id}: {e}")
        return None


def extract_audio_url(html_content):
    # Extract audio URL from the playAudio function
    match = re.search(r"playAudio\('(.*?)'\)", html_content)
    if match:
        return match.group(1)
    return None


def download_audio(url, lesson_num):
    # Format lesson number with leading zeros
    lesson_num_formatted = f"{lesson_num:03d}"
    file_path = f"audio/{lesson_num_formatted}.mp3"

    # Skip if file already exists
    if os.path.exists(file_path):
        print(
            f"Audio file for lesson {lesson_num_formatted} already exists, skipping download")
        return True

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Downloaded audio for lesson {lesson_num_formatted}")
        return True
    except requests.exceptions.RequestException as e:
        print(
            f"Failed to download audio for lesson {lesson_num_formatted}: {e}")
        return False


def extract_vocabulary(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the words div
    words_div = soup.find('div', id='words')
    if not words_div:
        print("Could not find vocabulary words section")
        return None

    vocabulary = []

    # Find all word entries
    word_entries = words_div.find_all('div', class_='text-truncate')

    for entry in word_entries:
        word_data = {}

        # Extract word text
        word_link = entry.find('a', class_='text-lightblue')
        if word_link:
            word_data['text'] = word_link.text.strip()

        # Check if word is marked as important (has a * marker)
        danger_span = entry.find('span', class_='text-danger')
        word_data['isDanger'] = 1 if danger_span else 0

        # Extract phonetic
        phonetic_elem = entry.find('small', class_='text-gray')
        if phonetic_elem:
            phonetic_text = phonetic_elem.text
            # Remove the phonetic markers and clean up
            phonetic = phonetic_text.replace('/', '').strip()
            word_data['phonetic'] = f"/{phonetic}/"

        # Extract translation
        translation_small = entry.find_all('small')
        if len(translation_small) > 1:  # The second small tag contains the translation
            word_data['translation'] = translation_small[-1].text.strip()

        # Extract toggle (full definition)
        title_elem = entry.find('h4', class_='d-inline-block')
        if title_elem and title_elem.has_attr('title'):
            word_data['toggle'] = title_elem['title']

        if word_data.get('text'):  # Only add if we have the word text
            vocabulary.append(word_data)

    return vocabulary


def save_vocabulary(vocabulary, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(vocabulary, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving vocabulary to {filename}: {e}")
        return False


def extract_text_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the lesson div
    lesson_div = soup.find('div', id='lesson')
    if not lesson_div:
        print("Could not find lesson content div")
        return None, None

    # Extract the question
    question_div = soup.find('div', id='question')
    question_text = ""
    if question_div:
        # Find the span with bg-info class
        question_span = question_div.find('span', class_='bg-info')
        if question_span:
            question_text = question_span.text.strip()

    if not question_text:
        print("Warning: Could not find question text")

    english_lines = []
    chinese_lines = []

    # Add lesson title
    # Find the lesson title from the strong tag with class h5
    lesson_title_elem = soup.find('strong', class_='h5')
    if lesson_title_elem:
        # Extract the full title text, keeping all parts
        english_title = lesson_title_elem.text.strip()
        english_lines.append(english_title)
    else:
        print("Warning: Could not find lesson title")
        english_lines.append("[Missing title]")

    # Add question
    english_lines.append("First listen and then answer the question:")
    english_lines.append(question_text)

    # Translate question to Chinese using OpenAI API
    translated_question = translate_question(question_text)

    # Add lesson title in Chinese
    chinese_title_span = soup.find('span', class_='mx-2 text-gray')
    if chinese_title_span and lesson_title_elem:
        # Extract lesson number from the English title
        match = re.search(r"Lesson\s+(\d+)", lesson_title_elem.text)
        if match:
            lesson_number = match.group(1)
            chinese_title = f"Lesson {lesson_number} {chinese_title_span.text.strip()}"
            chinese_lines.append(chinese_title)
        else:
            # Fallback if number not found
            chinese_lines.append(f"Lesson {chinese_title_span.text.strip()}")
    else:
        print("Warning: Could not find Chinese lesson title")
        chinese_lines.append("[Missing title]")

    # Add instruction line in Chinese
    chinese_lines.append("先听录音，然后回答问题：")

    # Add translated question
    chinese_lines.append(translated_question)

    # Extract paragraphs
    paragraphs = lesson_div.find_all('p')
    for p in paragraphs:
        english_text = p.text.strip()
        english_lines.append(english_text)

        # Find the next Chinese div
        chinese_div = p.find_next('div', class_='chinese')
        if chinese_div:
            chinese_text = chinese_div.text.strip()
            chinese_lines.append(chinese_text)
        else:
            print(f"Warning: Missing Chinese translation for: {english_text}")
            chinese_lines.append(f"[Needs translation: {english_text}]")

    return english_lines, chinese_lines


def translate_question(question_text):
    if not question_text:
        return "[No question to translate]"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "You are a translator. Translate the English question to Chinese accurately."},
                    {"role": "user", "content": f"Translate this English question to Chinese: {question_text}"}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(
                f"Translation error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retrying
            else:
                return f"[Translation needed for: {question_text}]"


def save_text_file(lines, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(f"{line}\n")  # No # prefix
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False


def save_mapping(mapping, filename="lesson_mapping.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2)
        print(f"Saved lesson mapping to {filename}")
        return True
    except Exception as e:
        print(f"Error saving mapping to {filename}: {e}")
        return False


def load_mapping(filename="lesson_mapping.json"):
    if not os.path.exists(filename):
        return {}

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            # Convert keys from strings to integers
            return {int(k): v for k, v in mapping.items()}
    except Exception as e:
        print(f"Error loading mapping from {filename}: {e}")
        return {}


def process_lesson(lesson_id, lesson_num, mapping):
    print(f"Processing lesson {lesson_id} (#{lesson_num})")

    # Format lesson number with leading zeros
    lesson_num_formatted = f"{lesson_num:03d}"

    # Check if files already exist
    en_file = f"en/{lesson_num_formatted}.txt"
    zh_file = f"zh/{lesson_num_formatted}.txt"
    audio_file = f"audio/{lesson_num_formatted}.mp3"
    words_file = f"words/{lesson_num_formatted}.json"

    all_files_exist = all(os.path.exists(f)
                          for f in [en_file, zh_file, audio_file, words_file])

    if all_files_exist:
        print(
            f"Lesson {lesson_num_formatted} already fully processed, skipping")
        # Still update the mapping
        mapping[str(lesson_id)] = lesson_num
        return True

    html_content = get_lesson_content(lesson_id)
    if not html_content:
        return False

    success = True

    # Extract and download audio
    audio_url = extract_audio_url(html_content)
    if audio_url and not os.path.exists(audio_file):
        if not download_audio(audio_url, lesson_num):
            success = False
    elif not audio_url:
        print(f"Warning: Could not find audio URL for lesson {lesson_id}")
        success = False

    # Extract and save text content if needed
    if not os.path.exists(en_file) or not os.path.exists(zh_file):
        english_lines, chinese_lines = extract_text_content(html_content)
        if english_lines and chinese_lines:
            if not os.path.exists(en_file):
                if not save_text_file(english_lines, en_file):
                    success = False
            if not os.path.exists(zh_file):
                if not save_text_file(chinese_lines, zh_file):
                    success = False
            print(f"Saved text files for lesson {lesson_num_formatted}")
        else:
            print(
                f"Error: Could not extract text content for lesson {lesson_id}")
            success = False

    # Extract and save vocabulary if needed
    if not os.path.exists(words_file):
        vocabulary = extract_vocabulary(html_content)
        if vocabulary:
            if not save_vocabulary(vocabulary, words_file):
                success = False
            else:
                print(
                    f"Saved vocabulary file for lesson {lesson_num_formatted}")
        else:
            print(
                f"Warning: Could not extract vocabulary for lesson {lesson_id}")
            # Don't mark as failure, vocabulary might be missing for some lessons

    # Update mapping if at least partially successful
    if success:
        mapping[str(lesson_id)] = lesson_num

    return success


def main():
    # Load existing mapping
    mapping = load_mapping()

    # Starting with lesson 173 -> 001
    if '173' not in mapping:
        mapping['173'] = 1  # Lesson ID 173 corresponds to Lesson 001

    # Process lessons 173 to 244
    for lesson_id in range(173, 233):  # 245 is exclusive, so it will process 173-244
        # Calculate lesson_num
        if str(lesson_id) in mapping:
            lesson_num = mapping[str(lesson_id)]
        else:
            # Lesson number is lesson_id minus 172
            lesson_num = lesson_id - 172

        success = process_lesson(lesson_id, lesson_num, mapping)

        # Save mapping after each lesson (in case of interruption)
        save_mapping(mapping)

        # Add a small delay to avoid overwhelming the server
        time.sleep(2)

    print("Processing complete!")


if __name__ == "__main__":
    main()
