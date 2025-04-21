"""
逐個計算txt檔中，標題＋內文前25個字中出現公司次數最多的公司 ==> 作為事件對應公司，並將檔名和對應公司輸出至excel
"""
import pandas as pd
import os


def main():
    companies_csv_path = '/Users/alex/Desktop/Assay code/collect sp500 company list/sp500 stock output.csv' #要改路徑
    news_folder_path = '/Users/alex/Desktop/論文/我的論文/Data 146/others/106 and filtered news data exclude amzn拷貝' #要改路徑

    results = []
    companies_df = pd.read_csv(companies_csv_path, usecols=[1], header=None)
    company_names = companies_df.iloc[:, 0].tolist()
    
    file = [f for f in os.listdir(news_folder_path) if f.endswith('.txt')]
    sorted_files = sorted(file, key=lambda x: int(x.split('.')[0]))
    
    for filename in sorted_files:
        if filename.endswith(".txt"):
            file_path = os.path.join(news_folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                all_text = file.read()
                
            lines = [line.strip() for line in all_text.splitlines() if line.strip()]
            content_words = " ".join(lines).split()
            
            title = lines[0] if lines else ""
            body = content_words[:26] 
            text_to_check = title + ' ' + ' '.join(body)
            
            company_count = {company: text_to_check.count(f'{company} ') for company in company_names}
            most_common_company = max(company_count, key=company_count.get, default='No company matched')
            
            
            results.append((filename, most_common_company))
    
    results_df = pd.DataFrame(results, columns=['Filename', 'Company'])
    results_df.set_index('Filename', inplace=True)

    output_excel_path = '/Users/alex/Desktop/0511assay data測試/124 sample/內生性/firm_list.xlsx' #要改路徑
    results_df.to_excel(output_excel_path)

if __name__ == "__main__":
    main()
