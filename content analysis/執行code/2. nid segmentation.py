'''
根據nid編號進行新聞切割，個別儲存成一個excel
'''
import pandas as pd
import os

# 設定檔案路徑
file_path = '/Users/alex/Desktop/0511assay data測試/124 sample/情緒分析變數/label result2.xlsx'
df = pd.read_excel(file_path)

output_dir = '/Users/alex/Desktop/0511assay data測試/124 sample/情緒分析變數/output'
os.makedirs(output_dir, exist_ok=True)

# 根據filter欄位值分組並存儲為單獨的Excel檔案
for filter_value in df['filter'].unique():
    # 根據filter值過濾資料
    filtered_df = df[df['filter'] == filter_value]
    
    # 設定輸出檔名
    output_file = os.path.join(output_dir, f'{filter_value}.xlsx')
    
    # 將過濾後的資料存儲為新的Excel檔案
    filtered_df.to_excel(output_file, index=False)

print("分割完成")
