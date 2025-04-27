import os
import glob


def insert_instruction_line():
    """Insert the missing instruction line in all Chinese text files."""
    # The instruction line to insert after the title
    instruction_line = "先听录音，然后回答问题："

    # Get all zh/*.txt files
    zh_files = glob.glob('zh/*.txt')
    print(f"Found {len(zh_files)} Chinese text files.")

    fixed_count = 0
    for file_path in zh_files:
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Check if the file already has the instruction line
            if len(lines) >= 2 and instruction_line in lines[1]:
                print(f"File {file_path} already has the instruction line.")
                continue

            # Insert the instruction line after the first line (after the title)
            if len(lines) > 0:
                updated_lines = [lines[0], f"{instruction_line}\n"]
                # Add the rest of the lines
                updated_lines.extend(lines[1:])

                # Write the updated content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)

                print(f"Fixed file: {file_path}")
                fixed_count += 1
            else:
                print(f"Warning: {file_path} is empty or has no lines.")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"Fixed {fixed_count} files successfully.")


if __name__ == "__main__":
    insert_instruction_line()
