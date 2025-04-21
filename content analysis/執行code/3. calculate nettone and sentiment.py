'''
計算每個模型的net tone and sentiment power，並將各模型結果存在一個excel中的不同sheet
'''

import os
import pandas as pd

def calculate_net_tone_and_power(data, label_column):
    positive = negative = neutral = 0
    total = len(data['sentence'])
    # print(f'total:{total}')
    for value in data[label_column]:
        if value == "Positive":
            positive += 1
        elif value == "Negative":
            negative += 1
        elif value == "Neutral":
            neutral += 1

    freq_positive = (positive / total) * 100
    freq_negative = (negative / total) * 100
    pos = positive/total
    neg = negative/total
    print(f'positive: {pos}')
    if freq_positive + freq_negative > 0:
        nettone = round(((freq_positive - freq_negative) / (freq_positive + freq_negative)), 3)
        sentiment_power = round(((freq_positive + freq_negative) / 100), 3)
        # print(f'nettone: {nettone}', f'sentiment_power: {sentiment_power}', '\n\n')
    else:
        nettone = sentiment_power = 0

    return  nettone, sentiment_power, pos, neg

def calculate_variables(data, columns_to_analyze):
    results = {}
    for column in columns_to_analyze:
        net_tone, sentiment_power, pos, neg = calculate_net_tone_and_power(data, column)
        results[column + '_net_tone'] = round(net_tone, 3)
        results[column + '_sentiment_power'] = round(sentiment_power, 3)
        results[column + '_freq(positive)'] = round(pos, 3)
        results[column + '_freq(negative)'] = round(neg, 3)
    
    return results

def main():
    directory_path = '/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/情緒分析變數/labeled result'
    files = [f for f in os.listdir(directory_path) if f.endswith('.xlsx')]
    sorted_files = sorted(files, key=lambda x: int(x.split('.')[0]))

    num_files = len(sorted_files)
    columns_to_analyze = ['final label', 'BiLSTM Label', 'BERT Label', 'FinBERT Label', 'FinBERT_ESGCalls Label', 'LM label']

    output_file_path = '/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/情緒分析變數/nettone_and_sentimentpower with pos and neg.xlsx'

    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        for column in columns_to_analyze:
            result_columns = [column + '_net_tone', column + '_sentiment_power', column + '_freq(positive)', column + '_freq(negative)']

            all_results = pd.DataFrame(index=range(1, num_files + 1), columns=result_columns)

            for idx, filename in enumerate(sorted_files):
                filepath = os.path.join(directory_path, filename)
                data = pd.read_excel(filepath)
                print(idx + 1)
                file_results = calculate_variables(data, [column])
                all_results.iloc[idx] = [file_results[column + '_net_tone'], file_results[column + '_sentiment_power'],
                                         file_results[column + '_freq(positive)'], file_results[column + '_freq(negative)']]
            
            all_results.to_excel(writer, sheet_name=column, index=False)

if __name__ == "__main__":
    main()
