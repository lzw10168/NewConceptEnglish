import json
import os
from pathlib import Path

def flatten_content(json_data):
    # 保存content之外的顶层键值
    flattened = {k: v for k, v in json_data.items() if k != 'content'}
    
    # 将content内的所有内容合并到顶层
    if 'content' in json_data:
        flattened.update(json_data['content'])
    # 把dialogueText = dialogueText[0]
    if 'dialogueText' in json_data:
        flattened['dialogueText'] = json_data['dialogueText'][0]
    if 'translation' in json_data:
        flattened['translation'] = json_data['translation'][0]
    return flattened

def process_directory(directory_path):
    # 转换为Path对象
    dir_path = Path(directory_path)
    
    # 确保目录存在
    if not dir_path.exists():
        print(f"目录 {directory_path} 不存在!")
        return
    
    # 获取所有json文件
    json_files = list(dir_path.glob("*.json"))
    
    if not json_files:
        print(f"在 {directory_path} 中没有找到JSON文件!")
        return
    
    # 处理每个文件
    for json_file in json_files:
        try:
            print(f"处理文件: {json_file.name}")
            
            # 读取JSON文件
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 扁平化处理
            flattened_data = flatten_content(data)
            
            # 写回原文件
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(flattened_data, f, ensure_ascii=False, indent=2)
            
            print(f"成功处理: {json_file.name}")
            
        except json.JSONDecodeError:
            print(f"错误: {json_file.name} 不是有效的JSON文件")
        except Exception as e:
            print(f"处理 {json_file.name} 时发生错误: {str(e)}")

if __name__ == "__main__":
    directory = "NCE1/json"
    print(f"开始处理目录: {directory}")
    process_directory(directory)
    print("处理完成!")



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
#     json_dir = Path('NCE2/json')
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
            
#             # 检查并更新 newwords.notes 字段
#             if 'newwords' in file_data and isinstance(file_data['newwords'], dict):
#                 print('file_name: ', file_name, vocabulary_data[file_name]['words'])
#                 file_data['newwords']['notes'] = vocabulary_data[file_name]['words']
#             else:
#                 file_data['newwords'] = {'notes': vocabulary_data[file_name]['words']}

#             # 保存更新后的文件
#             with open(json_file, 'w', encoding='utf-8') as f:
#                 json.dump(file_data, f, ensure_ascii=False, indent=2)
            
#             print(f"已完成文件：{json_file}")

#         except Exception as e:
#             print(f"处理文件 {json_file} 时出错：{str(e)}")

# if __name__ == '__main__':
#     update_newwords_notes()
# 
