import os

# 讀取文件的前三行
def read_first_three_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [next(file) for _ in range(3)]
        return ''.join(lines)

# 移除有相同前三行的文件
def remove_duplicates(directory_path):
    files_to_remove = set()
    first_three_lines_dict = {}

    txt_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.txt')]

    for file_path in txt_files:
        if file_path in files_to_remove:
            continue
        try:
            first_three_lines = read_first_three_lines(file_path)
            # print(first_three_lines)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue
        
        if first_three_lines in first_three_lines_dict:
            files_to_remove.add(file_path)
        else:
            first_three_lines_dict[first_three_lines] = file_path

    for file_path in files_to_remove:
        os.remove(file_path)
        print(f"Removed {file_path}")

    return files_to_remove


directory_path = '/Users/alex/Desktop/0511assay data測試/0512 news sample'  # 更改為你的文件路徑


remove_duplicates(directory_path)