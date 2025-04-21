"""

"""
import pandas as pd
from linearmodels.iv import IV2SLS
import statsmodels.api as sm



df1 = pd.read_excel('/Users/alex/Desktop/情緒回歸與內生性/LM CAR.xlsx') # 記得改路徑
df1.index = df1.index + 1

df1.drop(['FinBERT_FinNews Negative', 'EVENT', 'FinBERT_FinNews Positive'], axis=1, inplace=True)
df1 = df1.rename(columns={"FinBERT_FinNews log(Net Tone)" : 'log(Net Tone)',
                          'FinBERT_FinNews log(Sentiment Power)' : 'log(Sentiment Power)'}).round(4)



### 工具變數法（IV法) two stage ==> 比較預測內生變數＆原內生變數跑迴歸的結果
###  原始模型：CAR = b0 + b1*log(Net Tone) + b2*log(Sentiment Power)

# stage1：使用工具變數 log(positive) 預測內生變數 log(Net Tone)
first_stage = sm.OLS(df1['log(Net Tone)'], sm.add_constant(df1[['log(positive)', 'log(Sentiment Power)']])).fit()
df1['log(Net Tone)_predic'] = first_stage.predict(sm.add_constant(df1[['log(positive)', 'log(Sentiment Power)']]))

# Stage2：使用Stage1預測值 log(Net Tone)_predic 和外生變數 log(Sentiment Power)
second_stage = sm.OLS(df1['CAR'], sm.add_constant(df1[['log(Net Tone)_predic', 'log(Sentiment Power)']])).fit()

original = sm.OLS(df1['CAR'], sm.add_constant(df1[['log(Net Tone)', 'log(Sentiment Power)']])).fit()



### 控制變數法（CF法）==> 設殘差項為新變數後跑迴歸，若殘差變數的係數有顯著則存在內生性問題，若無則否 (Durbin–Wu–Hausman 檢定方法)
### 修正後模型：CAR = b0 + b1*log(Net Tone) + b2*log(Sentiment Power) + b3*Inverse Mills ratio(residual)

df1['Inverse Mills Ratio'] = df1['log(Net Tone)'] - df1['log(Net Tone)_predic'] # 計算殘差項 Inverse Mills Ratio
dwh_test = sm.OLS(df1['CAR'], sm.add_constant(df1[['log(Net Tone)_predic', 'log(Sentiment Power)', 'Inverse Mills Ratio']])).fit() # 將殘差項設為新變數加入迴歸式



### 不同工具變數測試，需檢測工具變數對內生變數 log(Net Tone) 有無顯著 ==> 需有顯著才能設為工具變數

df2 = sm.OLS(df1['log(Net Tone)'], sm.add_constant(df1['before COVID'])).fit() # 設工具變數為「before or after COVID」
print(df2.summary())

df3 = sm.OLS(df1['log(Net Tone)'], sm.add_constant(df1['log(positive)'])).fit() # 假設工具變數為「log(positive)」
print(df3.summary(), '\n')


print('original OLS', '\n', original.summary(), '\n') # 原始 OLS 結果
print('IV method', second_stage.summary(), '\n') # IV method結果
print('CF method','\n','--- DWH Test ---', '\n', dwh_test.summary(), '\n') # CF method結果

 

### 計算相關係數矩陣＆VIF test ==> 檢測變數間有無共線性問題

correlation_matrix = df1[['CAR', 'log(Net Tone)', 'log(Sentiment Power)']].corr()

print(correlation_matrix)
