 


import requests
from bs4 import BeautifulSoup, NavigableString
import os
import json
import re
# from ha85Crawler import get_vocabulary  # 导入get_vocabulary函数

# 新概念英语 自学导读 标签列表
tag_list_map = {
    'course-1-001': {
        "tags": [
            "一般疑问句",
            "自然拼读",
        ],
        "title": "1&2 Excuse me!",
        "id": "course-1-001",
    },
}

class NCEScraper:
    def __init__(self, base_url="http://www.newconceptenglish.com"):
        self.base_url = base_url
        self.session = requests.Session()
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("audio/nce3", exist_ok=True)
        # self.get_vocabulary = get_vocabulary  # 保存为实例方法

    def download_mp3(self, mp3_url, lesson_id):
        """Download the MP3 file for a lesson"""
        try:
            response = self.session.get(f"{self.base_url}/{mp3_url}")
            if response.status_code == 200:
                file_path = f"audio/nce3/{lesson_id}.mp3"
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return file_path
        except Exception as e:
            print(f"Error downloading audio: {e}")
        return None

    def extract_text_content(self, element):
        """Extract text content preserving line breaks"""
        # Check if element is a NavigableString (direct text node)
        if isinstance(element, str) or isinstance(element, NavigableString):
            return element.strip()
            
        if not element:
            return ""
            
        content = []
        for item in element.contents:
            if isinstance(item, str):
                if item.strip():
                    content.append(item.strip())
            elif item.name == "br":
                content.append("\n")
            elif item.name in ["p", "h3", "h4"]:
                content.append(item.get_text(strip=True))
                content.append("\n")
            else:
                content.append(item.get_text(strip=True))
                
        return "".join(content).strip()

    def parse_notes_section(self, div):
        """Parse notes section with <strong> headings and paragraph children"""
        notes_structure = []
        current_note = None
        
        # Find all paragraph elements
        paragraphs = div.find_all('p')
        
        for p in paragraphs:
            # Some sections have the heading in a strong tag
            strong_tag = p.find('strong')
            
            # Check if this paragraph contains a <strong> tag (which indicates a heading)
            if strong_tag:
                # If we have a previous note with content, add it to the result
                if current_note:
                    notes_structure.append(current_note)
                
                # Create a new note with this heading
                heading_text = strong_tag.get_text(strip=True)
                
                # Remove the strong tag content from the paragraph text to avoid duplication
                p_text = p.get_text(strip=True)
                if heading_text in p_text:
                    # Get the text after the heading to see if there's additional content in same paragraph
                    remaining_text = p_text[p_text.index(heading_text) + len(heading_text):].strip()
                    
                    current_note = {
                        "heading": heading_text,
                        "children": [remaining_text] if remaining_text else []
                    }
                else:
                    current_note = {
                        "heading": heading_text,
                        "children": []
                    }
            elif current_note:
                # This is a child paragraph of the current note
                child_text = p.get_text(strip=True)
                if child_text:  # Only add non-empty paragraphs
                    current_note["children"].append(child_text)
        
        # Add the last note if there is one
        if current_note:
            notes_structure.append(current_note)
            
        return notes_structure

    def process_section_content(self, div):
        """Process a content div and extract structured data"""
        result = []
        current_heading = None
        content_buffer = []
        
        for elem in div.children:
            if elem.name in ["h3", "h4"]:
                # Save previous heading content
                if current_heading and content_buffer:
                    result.append({
                        "heading": current_heading,
                        "content": "\n".join(content_buffer)
                    })
                    content_buffer = []
                
                current_heading = elem.get_text(strip=True)
                if "新概念英语－" in current_heading:
                    current_heading = current_heading.replace("新概念英语－", "")
            elif elem.name in ["p", "div"] or (isinstance(elem, str) and elem.strip()):
                if current_heading:
                    text = self.extract_text_content(elem)
                    if text:
                        content_buffer.append(text)
                        
        # Add the last section
        if current_heading and content_buffer:
            result.append({
                "heading": current_heading,
                "content": "\n".join(content_buffer)
            })
            
        return result

    def scrape_lesson(self, lesson_id):
        """Scrape a lesson page and extract all relevant content"""
        try:
            response = self.session.get(f"{self.base_url}/index.php?id={lesson_id}")
            if response.status_code != 200:
                print(f"Failed to fetch lesson: {lesson_id}, status code: {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract course title and subtitle
            course_title_div = soup.find("div", id="coursetitle")
            if not course_title_div:
                print(f"Could not find course title div for lesson: {lesson_id}")
                return None
                
            # Extract title parts
            title_parts = [text for text in course_title_div.stripped_strings]
            english_title = title_parts[0] if len(title_parts) > 0 else ""
            chinese_title = title_parts[1] if len(title_parts) > 1 else ""
            
            # Extract lesson info from span
            lesson_info = course_title_div.find("span").text if course_title_div.find("span") else ""
            
            # Extract audio URL
            audio_tag = soup.find("audio")
            print(audio_tag)
            audio_source = audio_tag.find("source")["src"] if audio_tag and audio_tag.find("source") else None
            audio_path = None
            if audio_source:
                audio_path = self.download_mp3(audio_source, lesson_id.split("-")[-1])
            
            # Extract tape question
            tape_question_div = soup.find("div", id="tapequestion")
            tape_question = {
                "question": "",
                "translation": ""
            }
            if tape_question_div and tape_question_div.get_text(strip=True):
                question_text = tape_question_div.get_text(strip=True)
                match = re.search(r'(.*?)(\s*[\u4e00-\u9fff].*)$', question_text)
                if match:
                    tape_question["question"] = match.group(1).replace("新概念英语－听录音，并回答问题", "").strip()
                    tape_question["translation"] = match.group(2).strip()
                
            # Find article content
            article = soup.find("article", class_="article-nce")
            if not article:
                print(f"Could not find article content for lesson: {lesson_id}")
                return None
                
            # Initialize structured_content - 移除vocabulary字段
            structured_content = {
                "editorNotes": "",            # 小编笔记
                "dialogueText": [],           # 课文 - the actual lesson dialogue
                "translation": [],            # 翻译
                "notesOnText": {},            # 课文详注
                "grammarNotes": {},           # 语法
                "wordStudy": {},              # 词汇学习
                "vocabulary": {}              # 词汇
            }
            
            # Keep track of divs we've already processed
            processed_divs = set()
            
            # Process the special sections first
            nce_divs = article.find_all("div", class_="nce")
            
            # Process 课文详注 (Notes on text)
            for div in nce_divs:
                section_h3 = div.find("h3")
                if section_h3 and ("详注" in section_h3.get_text() or "notes on the text" in section_h3.get_text().lower()):
                    notes = self.parse_notes_section(div)
                    structured_content["notesOnText"] = {
                        "heading": section_h3.get_text(strip=True),
                        "notes": notes
                    }
                    # Mark this div as processed
                    processed_divs.add(div)
                    break
            
            # Process 语法 (Grammar)
            for div in nce_divs:
                section_h3 = div.find("h3")
                if section_h3 and ("语法" in section_h3.get_text() or "grammar" in section_h3.get_text().lower()):
                    notes = self.parse_notes_section(div)
                    structured_content["grammarNotes"] = {
                        "heading": section_h3.get_text(strip=True),
                        "notes": notes
                    }
                    # Mark this div as processed
                    processed_divs.add(div)
                    break
            
            # Process 词汇学习 (Word study)
            for div in nce_divs:
                section_h3 = div.find("h3")
                if section_h3 and ("词汇" in section_h3.get_text() or "word study" in section_h3.get_text().lower()):
                    notes = self.parse_notes_section(div)
                    structured_content["wordStudy"] = {
                        "heading": section_h3.get_text(strip=True),
                        "notes": notes
                    }
                    # Mark this div as processed
                    processed_divs.add(div)
                    break
            
            # Process content by sections for other types of content
            content_sections = []
            current_section = None
            
            for element in article.children:
                if element.name == "div" and "nce-section-title" in element.get("class", []):
                    current_section = {
                        "sectionTitle": element.get_text(strip=True).replace("新概念英语 - ", ""),
                        "content": []
                    }
                    content_sections.append(current_section)
                elif element.name == "div" and "nce" in element.get("class", []) and current_section:
                    # Skip divs we've already processed
                    if element not in processed_divs:
                        current_section["content"].extend(self.process_section_content(element))
            
            # Process other sections
            for section in content_sections:
                for content_item in section["content"]:
                    heading = content_item["heading"].lower() if content_item["heading"] else ""
                    
                    if "笔记" in section["sectionTitle"]:
                        structured_content["editorNotes"].append(content_item)
                    elif "课文" in heading:
                        # Process lesson text into a list of dialogue lines
                        lines = content_item["content"].split('\n')
                        dialogue_lines = [line for line in lines if line.strip()]
                        structured_content["dialogueText"].append({
                            "heading": content_item["heading"],
                            "dialogue": dialogue_lines
                        })
                    elif "翻译" in heading:
                        # Process translation into a list of lines
                        lines = content_item["content"].split('\n')
                        translation_lines = [line for line in lines if line.strip()]
                        structured_content["translation"].append({
                            "heading": content_item["heading"],
                            "lines": translation_lines
                        })
                    # elif not ("详注" in heading or "语法" in heading or "词汇" in heading):
                    #     # Don't process sections we already handled
                    #     structured_content["additionalContent"].append(content_item)
            
            # 在构建lesson_data之前，获取vocabulary数据
            # vocabulary_json = self.get_vocabulary(lesson_id)
            # vocabulary_data = json.loads(vocabulary_json)
            # vocabulary_data["heading"] = "相关词汇 Related words"
            # structured_content["vocabulary"] = vocabulary_data
            
            lesson_data = {
                "id": lesson_id,
                "lessonNumber": lesson_id.split("-")[-1],
                "title": {
                    "english": english_title,
                    "chinese": chinese_title
                },
                "lessonInfo": lesson_info,
                "audioPath": audio_path,
                "listeningQuestion": tape_question,
                "content": structured_content,
            }
            
            # Save to JSON file
            # with open(f"data/nce1/{lesson_id}.json", "w", encoding="utf-8") as f:
                # json.dump(lesson_data, f, ensure_ascii=False, indent=2)
                
            return lesson_data
            
        except Exception as e:
            print(f"Error scraping lesson {lesson_id}: {e}")
            return None

    def scrape_all_lessons(self, lesson_ids):
        """Scrape multiple lessons"""
        results = []
        for lesson_id in lesson_ids:
            print(f"Scraping lesson: {lesson_id}")
            result = self.scrape_lesson(lesson_id)
            if result:
                results.append(result)
        return results

# Example usage
if __name__ == "__main__":
    # List of lesson IDs
    lesson_ids = [
        "course-3-001",
        "course-3-002",
        "course-3-003",
        "course-3-004",
        "course-3-005",
        "course-3-006",
        "course-3-007",
        "course-3-008",
        "course-3-009",
        "course-3-010",
        "course-3-011",
        "course-3-012",
        "course-3-013",
        "course-3-014",
        "course-3-015",
        "course-3-016",
        "course-3-017",
        "course-3-018",
        "course-3-019",
        "course-3-020",
        "course-3-021",
        "course-3-022",
        "course-3-023",
        "course-3-024",
        "course-3-025",
        "course-3-026",
        "course-3-027",
        "course-3-028",
        "course-3-029",
        "course-3-030",
        "course-3-031",
        "course-3-032",
        "course-3-033",
        "course-3-034",
        "course-3-035",
        "course-3-036",
        "course-3-037",
        "course-3-038",
        "course-3-039",
        "course-3-040",
        "course-3-041", 
        "course-3-042",
        "course-3-043",
        "course-3-044",
        "course-3-045",
        "course-3-046",
        "course-3-047",
        "course-3-048",
        "course-3-049",
        "course-3-050",
        "course-3-051",
        "course-3-052",
        "course-3-053",
        "course-3-054",
        "course-3-055",
        "course-3-056",
        "course-3-057",
        "course-3-058",
        "course-3-059",
        "course-3-060",
        
    ]
    
    scraper = NCEScraper()
    
    # Scrape a single lesson
    # lesson_data = scraper.scrape_lesson("course-2-001")
    # if lesson_data:
    #     print(f"Scraped lesson: {lesson_data['title']['english']} - {lesson_data['title']['chinese']}")
    #     print(f"Audio downloaded to: {lesson_data['audioPath']}")
    #     print(f"Data saved to: data/{lesson_data['id']}.json")
    
    # Uncomment to scrape all lessons
    results = scraper.scrape_all_lessons(lesson_ids)
    print(f"Scraped {len(results)} lessons successfully")
