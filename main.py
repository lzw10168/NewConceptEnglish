import json
import os
from pathlib import Path

# def flatten_content(json_data):
#     # 保存content之外的顶层键值
#     flattened = {k: v for k, v in json_data.items() if k != 'content'}
    
#     # 将content内的所有内容合并到顶层
#     if 'content' in json_data:
#         flattened.update(json_data['content'])
#     # 把dialogueText = dialogueText[0]
#     if 'dialogueText' in json_data:
#         flattened['dialogueText'] = json_data['dialogueText'][0]
#     if 'translation' in json_data:
#         flattened['translation'] = json_data['translation'][0]
#     return flattened

# def process_directory(directory_path):
#     # 转换为Path对象
#     dir_path = Path(directory_path)
    
#     # 确保目录存在
#     if not dir_path.exists():
#         print(f"目录 {directory_path} 不存在!")
#         return
    
#     # 获取所有json文件
#     json_files = list(dir_path.glob("*.json"))
    
#     if not json_files:
#         print(f"在 {directory_path} 中没有找到JSON文件!")
#         return
    
#     # 处理每个文件
#     for json_file in json_files:
#         try:
#             print(f"处理文件: {json_file.name}")
            
#             # 读取JSON文件
#             with open(json_file, 'r', encoding='utf-8') as f:
#                 data = json.load(f)
            
#             # 扁平化处理
#             flattened_data = flatten_content(data)
            
#             # 写回原文件
#             with open(json_file, 'w', encoding='utf-8') as f:
#                 json.dump(flattened_data, f, ensure_ascii=False, indent=2)
            
#             print(f"成功处理: {json_file.name}")
            
#         except json.JSONDecodeError:
#             print(f"错误: {json_file.name} 不是有效的JSON文件")
#         except Exception as e:
#             print(f"处理 {json_file.name} 时发生错误: {str(e)}")

# if __name__ == "__main__":
#     directory = "NCE1/json"
#     print(f"开始处理目录: {directory}")
#     process_directory(directory)
#     print("处理完成!")



# lesson_tags = [
#     ["学习指南"],  # Lesson 0 (75)
#     ["简单句"],  # Lesson 1 (76)
#     ["现在进行时", "一般现在时"],  # Lesson 2 (77)
#     ["一般过去时", "主谓双宾"],  # Lesson 3 (78)
#     ["现在完成时", "同位语"],  # Lesson 4 (79)
#     ["现在完成时", "一般过去时"],  # Lesson 5 (80)
#     ["冠词"],  # Lesson 6 (81)
#     ["过去进行时", "过去将来时"],  # Lesson 7 (82)
#     ["形容词", "副词", "比较级", "最高级"],  # Lesson 8 (83)
#     ["介词"],  # Lesson 9 (84)
#     ["被动语态"],  # Lesson 10 (85)
#     ["时态", "动词不定式"],  # Lesson 11 (86)
#     ["一般将来时"],  # Lesson 12 (87)
#     ["将来进行时", "名词所有格"],  # Lesson 13 (88)
#     ["过去完成时"],  # Lesson 14 (89)
#     ["直接引语", "间接引语", "宾语从句"],  # Lesson 15 (90)
#     ["if条件状语从句", "状语从句", "主将从现"],  # Lesson 16 (91)
#     ["情态动词", "must"],  # Lesson 17 (92)
#     ["have", "过去完成时"],  # Lesson 18 (93)
#     ["情态动词", "can", "may"],  # Lesson 19 (94)
#     ["动名词", "doing"],  # Lesson 20 (95)
#     ["被动语态", "情态动词"],  # Lesson 21 (96)
#     ["介词"],  # Lesson 22 (97)
#     ["时态", "There be", "单元复习"],  # Lesson 23 (98)
#     ["单元复习"],  # Lesson 24 (99)
#     ["并列句"],  # Lesson 25 (100)
#     ["宾语从句"],  # Lesson 26 (101)
#     ["put", "一般过去时"],  # Lesson 27 (102)
#     ["定语从句", "Be able to"],  # Lesson 28 (103)
#     ["表语从句"],  # Lesson 29 (104)
#     ["冠词", "结果状语从句"],  # Lesson 30 (105)
#     ["过去进行时", "一般过去时", "Used to do", "形式主语"],  # Lesson 31 (106)
#     ["同级比较"],  # Lesson 32 (107)
#     ["介词"],  # Lesson 33 (108)
#     ["被动语态"],  # Lesson 34 (109)
#     ["结果状语从句", "状语从句", "Used to do"],  # Lesson 35 (110)
#     ["一般将来时", "定语从句", "非限定性定语从句"],  # Lesson 36 (111)
#     ["将来完成时"],  # Lesson 37 (112)
#     ["过去完成时", "一般过去时", "让步状语从句"],  # Lesson 38 (113)
#     ["间接引语", "宾语从句"],  # Lesson 39 (114)
#     ["将来进行时", "虚拟条件句", "虚拟语气", "if条件状语从句"],  # Lesson 40 (115)
#     ["情态动词", "need", "情态动词词组"],  # Lesson 41 (116)
#     ["have", "过去完成时"],  # Lesson 42 (117)
#     ["主语从句", "can", "Be able to"],  # Lesson 43 (118)
#     ["doing", "动名词"],  # Lesson 44 (119)
#     ["被动语态"],  # Lesson 45 (120)
#     ["同位语从句"],  # Lesson 46 (121)
#     ["单元复习"],  # Lesson 47 (122)
#     ["单元复习"],  # Lesson 48 (123)
#     ["句型简化"],  # Lesson 49 (124)
#     ["定语", "状语"],  # Lesson 50 (125)
#     ["一般过去时"],  # Lesson 51 (126)
#     ["现在完成时", "现在完成进行时"],  # Lesson 52 (127)
#     ["一般过去时", "现在完成时", "现在完成进行时"],  # Lesson 53 (128)
#     ["冠词"],  # Lesson 54 (129)
#     ["非谓语动词", "Be used to do"],  # Lesson 55 (130)
#     ["比较级"],  # Lesson 56 (131)
#     ["介词"],  # Lesson 57 (132)
#     ["被动语态", "强调句"],  # Lesson 58 (133)
#     ["目的状语从句", "状语从句", "Used to do"],  # Lesson 59 (134)
#     ["一般将来时"],  # Lesson 60 (135)
#     ["将来进行时", "将来完成时", "将来完成进行时"],  # Lesson 61 (136)
#     ["过去完成时", "过去完成进行时"],  # Lesson 62 (137)
#     ["单元复习", "宾语从句"],  # Lesson 63 (138)
#     ["虚拟条件句", "if条件状语从句"],  # Lesson 64 (139)
#     ["情态动词词组", "情态动词的虚拟", "ought"],  # Lesson 65 (140)
#     ["have", "使役动词"],  # Lesson 66 (141)
#     ["Managed to do", "can", "Be able to"],  # Lesson 67 (142)
#     ["动名词", "反义疑问句", "非谓语动词"],  # Lesson 68 (143)
#     ["非谓语动词"],  # Lesson 69 (144)
#     ["形容词", "介词"],  # Lesson 70 (145)
#     ["单元复习"],  # Lesson 71 (146)
#     ["单元复习"],  # Lesson 72 (147)
#     ["简单句", "并列句", "复合句"],  # Lesson 73 (148)
#     ["非限定性定语从句"],  # Lesson 74 (149)
#     ["一般过去时"],  # Lesson 75 (150)
#     ["现在完成时", "现在完成进行时"],  # Lesson 76 (151)
#     ["一般过去时", "现在完成时", "现在完成进行时"],  # Lesson 77 (152)
#     ["冠词"],  # Lesson 78 (153)
#     ["倒装句", "部分倒装", "Be used to doing", "Used to do"],  # Lesson 79 (154)
#     ["比较级", "Be used to do"],  # Lesson 80 (155)
#     ["介词"],  # Lesson 81 (156)
#     ["被动语态"],  # Lesson 82 (157)
#     ["单元复习"],  # Lesson 83 (158)
#     ["单元复习", "一般将来时"],  # Lesson 84 (159)
#     ["将来完成进行时", "将来进行时", "一般将来时"],  # Lesson 85 (160)
#     ["过去完成时", "过去完成进行时"],  # Lesson 86 (161)
#     ["平行结构", "单元复习"],  # Lesson 87 (162)
#     ["if条件状语从句"],  # Lesson 88 (163)
#     ["情态动词", "分裂结构"],  # Lesson 89 (164)
#     ["have"],  # Lesson 90 (165)
#     ["can", "Be able to"],  # Lesson 91 (166)
#     ["doing", "否定前移"],  # Lesson 92 (167)
#     ["被动语态"],  # Lesson 93 (168)
#     ["单元复习"],  # Lesson 94 (169)
#     ["状语从句", "单元复习"],  # Lesson 95 (170)
#     ["单元复习"]  # Lesson 96 (171)
# ]

# # 保存为JSON文件
# import json

# with open('lesson_tags.json', 'w', encoding='utf-8') as f:
#     json.dump(lesson_tags, f, ensure_ascii=False, indent=2)

# import json
# import os
# from pathlib import Path

# def update_newwords_notes():
#     # 读取词汇参考数据
#     try:
#         with open('NCE2/all_vocabulary.json', 'r', encoding='utf-8') as f:
#             vocabulary_data = json.load(f)
#     except FileNotFoundError:
#         print("错误：找不到 all_vocabulary.json 文件")
#         return
#     except json.JSONDecodeError:
#         print("错误：all_vocabulary.json 文件格式不正确")
#         return

#     # 获取 NCE2/json 目录下的所有 json 文件并排序
#     json_dir = Path('/Users/Apple/Desktop/python/newConcept/data/nce2')
#     if not json_dir.exists():
#         print("错误：找不到 NCE2/json 目录")
#         return

#     # 获取所有json文件并按名称排序
#     json_files = sorted(json_dir.glob('*.json'))
    
#     # 顺序处理每个文件
#     for json_file in json_files:
#         try:
#             print(f"正在处理文件：{json_file}")
#             # 读取当前文件
#             with open(json_file, 'r', encoding='utf-8') as f:
#                 file_data = json.load(f)
            
#             # 获取文件名（不含扩展名）
#             file_name = json_file.stem
            
#             # 插入 tags
#             file_data['tags'] = lesson_tags[int(file_name.replace('lesson', ''))]
#             # 保存更新后的文件
#             with open(json_file, 'w', encoding='utf-8') as f:
#                 json.dump(file_data, f, ensure_ascii=False, indent=2)
            
#             print(f"已完成文件：{json_file}")

#         except Exception as e:
#             print(f"处理文件 {json_file} 时出错：{str(e)}")

# if __name__ == '__main__':
#     update_newwords_notes()



import os
import wave
from mutagen import File
from mutagen.mp3 import MP3
from pathlib import Path

def check_audio_file(file_path):
    """
    检查音频文件是否可以正常打开和读取
    返回 (是否正常, 错误信息)
    """
    try:
        # 获取文件扩展名
        ext = file_path.suffix.lower()
        
        if ext == '.wav':
            # 检查 WAV 文件
            with wave.open(str(file_path), 'rb') as wav_file:
                # 尝试读取文件参数
                frames = wav_file.getnframes()
                if frames <= 0:
                    return False, "WAV file has no frames"
                return True, "OK"
                
        elif ext == '.mp3':
            # 检查 MP3 文件
            audio = MP3(file_path)
            if audio.info.length <= 0:
                return False, "MP3 file has no duration"
            return True, "OK"
            
        else:
            return False, f"Unsupported file format: {ext}"
            
    except Exception as e:
        return False, str(e)

def scan_directory(directory_path):
    """
    扫描目录中的所有音频文件并检查其完整性
    """
    # 转换为 Path 对象
    dir_path = Path(directory_path)
    
    # 存储检查结果
    bad_files = []
    good_files = []
    
    # 遍历目录中的所有文件
    for file_path in dir_path.rglob('*'):
        if file_path.suffix.lower() in ['.wav', '.mp3']:
            is_good, error_msg = check_audio_file(file_path)
            
            if is_good:
                good_files.append(str(file_path.relative_to(dir_path)))
            else:
                bad_files.append((str(file_path.relative_to(dir_path)), error_msg))
    
    # 打印结果
    print(f"\nChecked {len(good_files) + len(bad_files)} audio files:")
    print(f"✅ {len(good_files)} files are good")
    print(f"❌ {len(bad_files)} files are corrupted\n")
    
    if bad_files:
        print("Corrupted files:")
        for file_path, error in bad_files:
            # delete
            os.remove(directory_path + '/' + file_path)
            print(f"- {file_path}")
            print(f"  Error: {error}")
    
    # 保存结果到文件
    with open('audio_check_results.txt', 'w', encoding='utf-8') as f:
        f.write("Audio File Check Results\n")
        f.write("=======================\n\n")
        
        f.write("Good Files:\n")
        for file in good_files:
            f.write(f"✅ {file}\n")
        
        f.write("\nCorrupted Files:\n")
        for file, error in bad_files:
            f.write(f"❌ {file}\n")
            f.write(f"   Error: {error}\n")

if __name__ == "__main__":
    # 使用你提供的目录路径
    directory = "/Users/Apple/Desktop/web/wasp-learning-english/app/public/audio/nce2"
    
    # 首先检查目录是否存在
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
    else:
        print(f"Scanning directory: {directory}")
        print("This may take a while depending on the number of files...")
        
        scan_directory(directory)
        
        print("\nDetailed results have been saved to 'audio_check_results.txt'")
