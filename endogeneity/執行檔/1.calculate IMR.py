'''
請將計算得出的Inverse mills ratio欄位資料, 整理到原CAR迴歸式的excel中
'''
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import Probit
import statsmodels.formula.api as smf

def main():
    path = '/Users/alex/Desktop/0511assay data測試/124 sample/內生性/內生性檢驗 firm list.xlsx'  # firm size and ROA的檔案（481 sample）
    df = pd.read_excel(path, sheet_name="sheet3")

    # 可新增檢測變數
    x1 = df[['market cap']]
    x2 = df[['ROA t-1']]

    # 設定第一階段的自變數（firm size和ROA t-1）和依變數（filter）
    X = df[['market cap', 'ROA t-1']]
    y = df['filter']

    # 檢測自變數是否對選擇變數有顯著影響
    p1 = Probit(y, x1).fit()
    print(p1.summary())

    p2 = Probit(y, x2).fit()
    print(p2.summary())

    # 執行Probit二元回歸
    probit_model = Probit(y, X).fit()

    # 預測IMR值
    df['IMR'] = probit_model.predict(X)
    print(df)
    
    df.to_excel('/Users/alex/Desktop/0511assay data測試/124 sample/內生性/內生性檢驗 with IMR test.xlsx', index=False, engine='openpyxl')
    print("IMR值已成功添加到Excel檔案中。")



if __name__ == "__main__":
    main()