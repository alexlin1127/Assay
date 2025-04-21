"""
遍歷每個txt檔，並抓最後五行中的提到的日期作為事件日，輸出至excel（輸出內容包含檔名和對應日期）
"""

import os
import re
import pandas as pd


def main():
    path = '/Users/alex/Desktop/論文/我的論文/Data 146/others/106 and filtered news data exclude amzn拷貝' # 變更為自己的路徑

    date_pattern = re.compile(r'(\d{4})/(\d{2})/(\d{2})')  # 2022/01/01 格式

    date_list = []
    files = [f for f in os.listdir(path) if f.endswith('.txt')]
    sorted_files = sorted(files, key=lambda x: int(x.split('.')[0]))

    for filename in sorted_files:
        if filename.endswith('.txt'):
            file_path = os.path.join(path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                content_to_check = ''.join(lines[-5:])
                
                matches = date_pattern.finditer(content_to_check)

                for match in matches:
                    try:
                        date_str = match.group(0)
                        date_list.append((filename, date_str))
                    except ValueError:
                        print('日期從缺')
                        pass
    
    result = pd.DataFrame(date_list, columns=['Filename', 'Event date'])
    result.set_index('Filename', inplace=True)
    result.to_excel('/Users/alex/Desktop/0511assay data測試/124 sample/內生性/內生性 news date.xlsx') # 變更檔名和路徑


if __name__ == '__main__':
    main()