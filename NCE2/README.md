# New Concept English Scraper

This script scrapes the New Concept English lessons from a website, downloads audio files, and extracts English and Chinese text as well as vocabulary words. The script is designed to process lessons 76-171, which correspond to actual lesson numbers 1-96.

## Features

- Downloads audio files for each lesson
- Extracts English text content
- Extracts Chinese translations
- Extracts vocabulary words with pronunciations and definitions
- Uses OpenAI API to translate questions that don't have Chinese translations
- Saves progress in a mapping file to resume interrupted scraping
- Handles errors gracefully with retries

## Requirements

Install the required packages:

```bash
pip install requests beautifulsoup4 openai
```

## Usage

1. Add your OpenAI API key to the script (edit the line `client = OpenAI(api_key="your-api-key-here")`)
2. Run the script:

```bash
python main.py
```

## Output

The script creates the following directories and files:

- `audio/` - Contains MP3 files for each lesson (format: `001.mp3`, `002.mp3`, etc.)
- `en/` - Contains English text files for each lesson (format: `001.txt`, `002.txt`, etc.)
- `zh/` - Contains Chinese text files for each lesson (format: `001.txt`, `002.txt`, etc.)
- `words/` - Contains vocabulary JSON files for each lesson (format: `001.json`, `002.json`, etc.)
- `lesson_mapping.json` - Maps between lesson IDs on the website and actual lesson numbers

## Vocabulary Format

Each vocabulary file contains an array of words with the following properties:

```json
[
  {
    "text": "private",
    "translation": "私人的",
    "phonetic": "/ˈpraɪvət/",
    "toggle": "adj. 私人的，私立的",
    "isDanger": 1
  },
  ...
]
```

- `text`: The word itself
- `translation`: Chinese translation
- `phonetic`: Pronunciation guide
- `toggle`: Complete definition with part of speech
- `isDanger`: Whether the word is marked as important (1 = yes, 0 = no)

## Customization

You can modify the script to:

- Change the range of lessons to scrape by modifying the `range(76, 172)` in the `main()` function
- Adjust the delay between requests by changing the `time.sleep(2)` value
- Use a different OpenAI model by changing the `model` parameter in the `translate_question()` function

## Troubleshooting

- If the script fails, it will automatically resume from where it left off when you run it again
- Check the console output for error messages and warnings
- If you encounter API rate limits, increase the sleep time between requests 
