import pandas as pd
import os

directory_path = '/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/情緒分析變數/labeled result'
files = [f for f in os.listdir(directory_path) if f.endswith('.xlsx')]
sorted_files = sorted(files, key=lambda x: int(x.split('.')[0]))

df = pd.DataFrame(columns=['filename', 'total_sentences'])

for i, filename in enumerate(sorted_files):
    filepath = os.path.join(directory_path, filename)
    data = pd.read_excel(filepath)
    total = len(data['sentence'])
    df.loc[i] = [filename, total]

output_filepath = '/Users/alex/Desktop/total_sentences.xlsx'
df.to_excel(output_filepath, index=False)
