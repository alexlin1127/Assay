""

""
import os

def get_specific_lines_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()[4:7]  
            return ''.join(lines).strip()  
    except IndexError:
        return None

directory_path = '/Users/alex/Desktop/0511assay data測試/0512 news sample'

txt_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]

content_to_file_map = {}
duplicates = []

for file in txt_files:
    content = get_specific_lines_content(os.path.join(directory_path, file))
    if content is None:
        continue
    if content in content_to_file_map:
        duplicates.append(file)
    else:
        content_to_file_map[content] = file

for duplicate in duplicates:
    os.remove(os.path.join(directory_path, duplicate))
    print(f'Removed {directory_path}/{duplicate}')
