"""

"""
import os
import re


def main():
    path = '/Users/alex/Desktop/0511assay data測試/126 v3 sample/0512 news sample'
    date_pattern = re.compile(r'\d{4}/\d{2}/\d{2}')
    for filename in os.listdir(path):
        if filename.endswith('.txt'):
            file_path = os.path.join(path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # 只檢查最後五行
                content_to_check = ''.join(lines[-5:])
                if date_pattern.search(content_to_check):
                    pass
                else:
                    print(filename)
                

if __name__ == '__main__':
    main()
