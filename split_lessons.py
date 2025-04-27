import os
import re

# Create the output directory if it doesn't exist
output_dir = 'NCE2/Lessons_Split'
os.makedirs(output_dir, exist_ok=True)

# Read the entire file
with open('NCE2/note2.txt', 'r', encoding='utf-8', errors='ignore') as file:
    content = file.read()

# Split the content by lesson
# Using a regex pattern to match "Lesson XX" at the beginning of a line
lesson_pattern = r'(?:\n|\r\n)(\s*Lesson\s+\d+\s+[^\n\r]+)'
matches = re.finditer(lesson_pattern, content)

# Keep track of where each lesson starts
lesson_starts = []
for match in matches:
    lesson_starts.append((match.start(), match.group(1).strip()))

# Extract and write each lesson
for i in range(len(lesson_starts)):
    start_pos, lesson_header = lesson_starts[i]
    
    # Extract lesson number
    lesson_num_match = re.search(r'Lesson\s+(\d+)', lesson_header)
    if lesson_num_match:
        lesson_num = lesson_num_match.group(1).strip()
        # Add leading zero for single digit lesson numbers
        if len(lesson_num) == 1:
            lesson_num = f"0{lesson_num}"
    else:
        lesson_num = f"{i+1:02d}"
    
    # Determine the end position - either the start of the next lesson or the end of the file
    end_pos = lesson_starts[i+1][0] if i < len(lesson_starts)-1 else len(content)
    
    # Extract the lesson content
    lesson_content = content[start_pos:end_pos]
    
    # Create the output file name
    output_file = os.path.join(output_dir, f"Lesson_{lesson_num}.txt")
    
    # Write the lesson to a file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(lesson_content)
    
    print(f"Created {output_file}")

print("Splitting complete!") 
