"""

"""
import os
import re
from datetime import datetime

date_patterns = [
    (re.compile(r'\b(\w{3}) (\d{2}), (\d{4})\b'), '%b %d, %Y'),  # Feb 07, 2022
    (re.compile(r'(\d{2})/(\d{2})/(\d{4})'), '%m/%d/%Y'),  # 10/01/2022
    (re.compile(r'(\d{4})/(\d{2})/(\d{2})'), '%Y/%m/%d')  # 2022/10/01
]

checked_dates = []

def convert_date_format(text): # 將新聞中日期全轉換成2022/10/01格式
    global checked_dates
    file_dates = []
    for pattern, date_format in date_patterns:
        matches = pattern.finditer(text)
        
        for match in matches:
            date_str = match.group(0)
            try:
                date_obj = datetime.strptime(date_str, date_format)
                new_date_str = date_obj.strftime('%Y/%m/%d')
                text = text.replace(date_str, new_date_str)
                file_dates.append(date_obj)
            except ValueError:
                print('date match error')
                pass
    return text, file_dates

def is_date_valid(file_dates):
    global checked_dates
    for date in file_dates:
        for checked_date in checked_dates:
            print(checked_date)
            if abs((date - checked_date).days) < 10: # 篩掉事件日相臨十天內的新聞，篩法：從頭排查事件日，重複者丟到issue date news folder
                return False
    return True

def has_date_in_last_lines(content):
    for pattern, _ in date_patterns:
        if pattern.search(content):
            return True
    return False

def process_files(input_dir, issue_dir_data):
    global checked_dates
    files_with_issues_data = []
    files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    sorted_files = sorted(files, key=lambda x: int(x.split('.')[0]))
    
    for filename in sorted_files:
        if filename.endswith('.txt'):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            content_to_check = ''.join(lines[-5:])
            move_file = False
            if has_date_in_last_lines(content_to_check):
                new_content_to_check, file_dates = convert_date_format(content_to_check)

                if not is_date_valid(file_dates):
                    move_file = True
                
                else: 
                    # if new_content_to_check != content_to_check:
                    #     new_content = ''.join(lines[:-5]) + new_content_to_check
                    checked_dates.extend(file_dates)
                        # with open(file_path, 'w', encoding='utf-8') as file:
                        #     file.write(new_content)

            else:
                move_file = True

            if move_file:
                files_with_issues_data.append(filename)
                os.rename(file_path, os.path.join(issue_dir_data, filename))

    return files_with_issues_data


def main():
    input_dir = r'/Users/alex/Desktop/0511assay data測試/0512 news sample' # 記得變更路徑
    issue_dir_data = r'/Users/alex/Desktop/0511assay data測試/issue date news' # 這個也要
    if not os.path.exists(issue_dir_data):
        os.makedirs(issue_dir_data)
    
    files_with_issues_data = process_files(input_dir, issue_dir_data)
    print(f"Files with issues (no dates or date problems): {files_with_issues_data}")



if __name__ == '__main__':
    main()
