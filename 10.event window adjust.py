import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import linregress
from scipy import stats
from scipy.stats import norm


# 讀取 Excel 檔 (請將路徑改為你電腦中的檔案路徑)
stock_data = pd.read_excel(r"/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Assay data/analysis data/part 1 事件研究法/stock data test.xlsx")
event = pd.read_excel(r"/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Assay data/analysis data/part 1 事件研究法/event list.xlsx")
market_return = pd.read_excel(r"/Users/alex/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Assay data/analysis data/part 1 事件研究法/sp500data test.xlsx")

# 變更 stock_data、market_return 索引值從1開始(原始值為0)
event.set_index('nid', inplace=True)
stock_data.index = stock_data.index + 1
market_return.index = market_return.index + 1
market_return['Date'] = pd.to_datetime(market_return['Date'])
stock_data['Date'] = pd.to_datetime(stock_data['Date'])

event_ret = pd.DataFrame()
sar = []
var_Si_total = 0


for i in range(1, len(event.index)+1):
    
    # 抓取事件日期
    event_date = datetime.strptime((event.loc[event.index[i - 1], 'Eventdate']), "%Y-%m-%d")

    # 抓取公司 Ticker
    ticker = event.loc[event.index[i - 1], 'Ticker']

    # 在 stock_data 中抓取該公司的股價資料
    ticker_i = pd.DataFrame(stock_data.loc[stock_data['Ticker'] == ticker, ['Ticker', 'Date', 'Ret']])
    ticker_i['Date'] = pd.to_datetime(ticker_i['Date'])

    ticker_i.reset_index(drop=True, inplace=True)
    ticker_i.index = ticker_i.index + 1
    

    """ 請先#52行之後內容，並執行以下檢查，若有error則需手動更改事件excel檔中的事件日（往後加一天）直至第一個事件日，排查完所有事件日後，在執行#60行後的內容"""
    # # 檢查有哪個事件日沒有交易日資料（事件日為假日，需手動將事件日往後加一天，直到有對應交易日資料）
    # date_list = [str(date.date()) for date in ticker_i['Date']]
    # if str(event_date.date()) in date_list:
    #     print(i, event_date)
    #     continue

    # else:
    #     print('error','\n', i, event_date)
    #     break

    ticker_i_value = pd.DataFrame(ticker_i.loc[ticker_i['Date'] == event_date, ['Ticker', 'Date', 'Ret']])

    # 事件日股價對應的資料筆數index值
    index = ticker_i_value[ticker_i_value['Date'] == event_date].index[0]

    # 取得估計期和事件期資料
    estimate_window_return = ticker_i.loc[index - 205 : index - 6, ['Ticker', 'Date', 'Ret']]  # 取得個股估計期資料
    event_window_return = ticker_i.loc[index - 10 : index + 10, ['Ticker', 'Date', 'Ret']]  # 取得個股事件期資料
    market_estimate_return = market_return.loc[index - 205 : index - 6, ['Date', 'MarketRet']]  # 取得市場估計期資料
    market_event_return = market_return.loc[index - 10 : index + 10, ['Date', 'MarketRet']]  # 取得市場事件期資料

    stocki_est_ret = estimate_window_return['Ret'].tolist()
    stocki_eve_ret = event_window_return['Ret'].tolist()
    mar_est_ret = market_estimate_return['MarketRet'].tolist()
    mar_eve_ret = market_event_return['MarketRet'].tolist()


    # 進行OLS回歸取得係數(y=a*x+b)
    OLS_result = linregress(mar_est_ret, stocki_est_ret)
    a = OLS_result.slope
    b = OLS_result.intercept


    # 計算預期報酬、異常報酬
    expected_ret = [round(x, 6) for x in [(x * a) + b for x in mar_eve_ret]]
    ar = zip(stocki_eve_ret, expected_ret)
    ar = [ x - y for x, y in ar ]
    ar = pd.DataFrame([round(z, 6) for z in ar], columns=[f'AR{i}'])
    ar.index = ar.index + 1

    event_window_return.reset_index(drop=True, inplace=True)
    event_window_return.index = event_window_return.index + 1


    # 將事件期第t日所有事件的AR值存到event_ret中
    event_ret = pd.concat([event_ret, ar], axis=1, ignore_index=False)
    

    # 計算公式 AR t test之sigma
    expected = [a * x + b for x in mar_est_ret]
    error = [stocki_est_ret[i] - expected[i] for i in range(len(expected))]
    err_mean = sum(error) / len(error)
    var_Si = sum([(x - err_mean) ** 2 for x in error]) / 199
    var_Si_total = var_Si_total + var_Si


    # 計算公式 SRM t test
    avr = sum(mar_est_ret) / 200 # 估計期天數200
    v1 = [(x - avr) ** 2 for x in mar_eve_ret]
    v2 = float(sum((y - avr) ** 2 for y in mar_est_ret))
    var_si_2 = sum([(x - err_mean) ** 2 for x in error]) / (200 - 2) # 自由度修正
    v3 = [(z / v2) for z in v1]
    var_ar_ie = [var_si_2 * (1 + 1/200 + c1)  for c1 in v3] 
    sigma_ar = [c ** 0.5 for c in var_ar_ie]
    sar.append(ar[f'AR{i}'] / sigma_ar)


# # 計算AR的平均和標準差
ar_means = round(event_ret.mean(axis=1) * 100, 3)
ar_stds = round(event_ret.std(axis=1), 3)
AR_ave = pd.DataFrame({ 'AR ave': ar_means, 'AR std': ar_stds })
# AR_ave.to_excel('/Users/alex/Desktop/News data/AR_ave.xlsx', index=True, engine='openpyxl')

print(event_ret)
print(event_ret.iloc[10])
ARday0 = event_ret.iloc[10]
event_ret.to_excel('/Users/alex/Desktop/AR.xlsx', index=True, engine='openpyxl')

### 公式計算 AR t test ###

n = len(event.index)
sigma_ar = (var_Si_total ** 0.5) / n

# 計算t檢定統計量
t_test = pd.DataFrame(round((event_ret.mean(axis=1) / sigma_ar), 3), columns=['Z_score']).reset_index(drop=True)

# 計算p value
p_value1 = pd.DataFrame((2 * norm.sf(abs(x)) for x in t_test['Z_score']), columns=['p_value'])

ar_ttest_fml = pd.concat([t_test, p_value1], axis=1, ignore_index=False)

def label_p_value(p):
    if p <= 0.01:
        return '***'
    elif 0.01 < p <= 0.05:
        return '**'
    elif 0.05 < p <= 0.1:
        return '*'
    else:
        return ''


ar_ttest_results = []
signtest = []
signed_rank_result = []
p = []


for index, row in event_ret.iterrows():

    # 將所有事件於事件期第t日的異常報酬率存在test_data
    test_data = pd.DataFrame(row.tolist(), columns=['test_data'], index=range(1, len(event.index) + 1))
    test_data['test_data'] = pd.to_numeric(test_data['test_data'])
    
    ### 套件計算 AR t test ###
    t, p_value = stats.ttest_1samp(test_data, 0)
    ar_ttest_results.append({'t_value': round(t[0], 3), 'p_value': p_value[0]})

    ### 公式計算 AR sign test ### (n>=20 以二項分布近似常態分佈( mu = np, var = np(1-p), p=0.5)
    count = 0
    for x in test_data['test_data']:
        if x > 0 : 
            count += 1

    s = max(count, n - count) # 取得 n 筆異常報酬中，正、負個數總合較大者（n=事件數）
    mu = n * 0.5
    sigma = (n ** 0.5) * 0.5

    # 計算 z_score 和 p_values，並判斷顯著性
    z_score = [round(((s - mu ) / sigma), 3)]
    p_value2 = [2 * (1 - stats.norm.cdf(z)) for z in z_score]

    signtest.append(z_score[0])
    p.append(p_value2[0])
    signtest_result = pd.DataFrame({'z_score': signtest, 'p_value' : p})

    ### 套件計算 AR Wilcoxon signed-rank test ### 
    result, p_value3 = stats.wilcoxon(test_data - 0 , zero_method = "wilcox", alternative = "two-sided")
    signed_rank_result.append({'t_value': result[0], 'p_value': p_value3[0]})

### 公式計算 AR SRM t test ###
sar = pd.DataFrame(sar)
sar_result = []

for column in sar:
    test1 = sum(sar[column])
    Ti = 200 #估計其天數
    sigma_sar = (((Ti - 2) / (Ti - 4)) * n) ** 0.5
    
    sar_t = round((test1 / sigma_sar), 3)
    sar_result.append(sar_t)


ar_ttest_result = pd.DataFrame(ar_ttest_results)
ar_ttest_result['significance'] = ar_ttest_result['p_value'].apply(label_p_value)
ar_ttest_result['相對天數'] = [i for i in range(-10, 11)]
ar_ttest_result.set_index('相對天數', inplace=True)

ar_ttest_fml['significance'] = ar_ttest_fml['p_value'].apply(label_p_value)
ar_ttest_fml['相對天數'] = [i for i in range(-10, 11)]
ar_ttest_fml.set_index('相對天數', inplace=True)

ar_srm_ttest = pd.DataFrame({'SRM t_value' : sar_result})
ar_srm_ttest['p_value'] = ar_srm_ttest['SRM t_value'].apply(lambda x: 2 * stats.t.sf(abs(x), df=19)) # 計算p value
ar_srm_ttest['significance'] = ar_srm_ttest['p_value'].apply(label_p_value)
ar_srm_ttest['相對天數'] = [i for i in range(-10, 11)]
ar_srm_ttest.set_index('相對天數', inplace=True)

signtest_result['significance'] = signtest_result['p_value'].apply(label_p_value)
signtest_result['相對天數'] = [i for i in range(-10, 11)]
signtest_result.set_index('相對天數', inplace=True)

signed_rank_result = pd.DataFrame(signed_rank_result)
signed_rank_result['significance'] = signed_rank_result['p_value'].apply(label_p_value)
signed_rank_result['相對天數'] = [i for i in range(-10, 11)]
signed_rank_result.set_index('相對天數', inplace=True)


### 套件計算 CAR t-test ###
# car_values = pd.DataFrame()
# for column in event_ret.columns:

#     # 檢測事件日之前，股價提前反映的情況，每個窗格間隔兩天為一單位
#     car_values.loc[column, 'car[-6 +0]'] = event_ret.loc[ 5:11, column].mean()  
#     car_values.loc[column, 'car[-4 +0]'] = event_ret.loc[ 7:11, column].mean()  
#     car_values.loc[column, 'car[-2 +0]'] = event_ret.loc[ 9:11, column].mean()

#     # 檢測事件日前後1-3天
#     car_values.loc[column, 'car[-1 +1]'] = event_ret.loc[10:12, column].mean()  
#     car_values.loc[column, 'car[-2 +2]'] = event_ret.loc[ 9:13, column].mean()  
#     car_values.loc[column, 'car[-3 +3]'] = event_ret.loc[ 8:14, column].mean()

#     car_values.loc[column, 'car[-4 +4]'] = event_ret.loc[ 7:15, column].mean()
#     car_values.loc[column, 'car[-5 +5]'] = event_ret.loc[ 6:16, column].mean()
#     car_values.loc[column, 'car[-10 +10]'] = event_ret.loc[ :, column].mean()

#     # 檢測事件日之後，股價才開始反應的情況，每個窗格間隔兩天為一單位
#     car_values.loc[column, 'car[+0 +2]'] = event_ret.loc[ 11:13, column].mean()
#     car_values.loc[column, 'car[+0 +4]'] = event_ret.loc[ 11:15, column].mean()  
#     car_values.loc[column, 'car[+0 +6]'] = event_ret.loc[ 11:17, column].mean()  
#     # 可自行新增事件窗格

# # print(car_values)
# # car_values.to_excel("/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/CAR windows data.xlsx", index=True, engine="openpyxl")
# # print('car value','\n', car_values)
# # # 計算累積平均異常報酬！
# car_means = round(car_values.mean(axis=0) * 100, 3)
# car_median = round(car_values.median(axis=0) * 100, 3)
# CAR_ave = pd.DataFrame({ 'CAR ave': car_means, 'CAR median': car_median})
# print('累加平均異常報酬', '\n', CAR_ave)
# # CAR_ave.to_excel('/Users/alex/Desktop/News data/CAR_ave.xlsx', index=True, engine='openpyxl')

# car_ttest = []
# car_signed_rank = []
# car_signtest = []

# for column in car_values.columns:

#     ### 套件計算 CAR t test ###
#     t_value, p_value4 = stats.ttest_1samp(car_values[column], 0)
#     car_ttest.append({'Column': column, 't_value': round(t_value, 3), 'p_value': round(p_value4, 3)})

#     ### 套件計算 CAR signed-rank test ###
#     sr, p_value5 = stats.wilcoxon(car_values[column] - 0, zero_method = "wilcox", alternative = "two-sided")
#     car_signed_rank.append({'Column' : column, 'SR' : round(sr, 3), 'p_value' : round(p_value5, 3)})

#     ### 公式計算 CAR sign test ###
#     count1 = 0
#     for x in car_values[column]:
#         if x > 0 : 
#             count1 += 1

#     s1 = max(count1, n - count1) # 取n筆累計異常報酬中，正、負個數總合較大者（n=事件數150）
#     mu1 = n * 0.5
#     sigma1 = (n ** 0.5) * 0.5

#     # 計算 z_score 和 p_values，並判斷顯著性
#     z_score1 = [round((s1 - mu1 ) / sigma1, 3)]
#     p_value6 = [round(2 * (1 - stats.norm.cdf(z)),3) for z in z_score1]

#     car_signtest.append({'Column' : column, "z_score" : z_score1[0], 'p_value' : p_value6[0]})

# sar = pd.DataFrame(sar).T
# scar_values = pd.DataFrame()

# for column in sar.columns:

#     # 檢測事件日之前，股價提前反映的情況，每個窗格間隔兩天為一單位
#     scar_values.loc[column, 'scar[-6 +0]'] = sum(sar.loc[ 5:11, column]) / (len(sar.loc[ 5:11, column]) ** 0.5)
#     scar_values.loc[column, 'scar[-4 +0]'] = sum(sar.loc[ 7:11, column]) / (len(sar.loc[ 7:11, column]) ** 0.5)
#     scar_values.loc[column, 'scar[-2 +0]'] = sum(sar.loc[ 9:11, column]) / (len(sar.loc[ 9:11, column]) ** 0.5)

#     # 檢測事件日前後1-3天
#     scar_values.loc[column, 'scar[-1 +1]'] = sum(sar.loc[10:12, column]) / (len(sar.loc[10:12, column]) ** 0.5)
#     scar_values.loc[column, 'scar[-2 +2]'] = sum(sar.loc[ 9:13, column]) / (len(sar.loc[ 9:13, column]) ** 0.5)
#     scar_values.loc[column, 'scar[-3 +3]'] = sum(sar.loc[ 8:14, column]) / (len(sar.loc[ 8:14, column]) ** 0.5)
    
#     scar_values.loc[column, 'scar[-4 +4]'] = sum(sar.loc[ 7:15, column]) / (len(sar.loc[ 7:15, column]) ** 0.5)
#     scar_values.loc[column, 'scar[-5 +5]'] = sum(sar.loc[ 6:16, column]) / (len(sar.loc[ 6:16, column]) ** 0.5)
#     scar_values.loc[column, 'scar[-10 +10]'] = sum(sar.loc[:, column]) / (len(sar.loc[ :, column]) ** 0.5)

#     # 檢測事件日之後，股價才開始反應的情況，每個窗格間隔兩天為一單位
#     scar_values.loc[column, 'scar[+0 +2]'] = sum(sar.loc[11:13, column]) / (len(sar.loc[11:13, column]) ** 0.5)
#     scar_values.loc[column, 'scar[+0 +4]'] = sum(sar.loc[11:15, column]) / (len(sar.loc[11:15, column]) ** 0.5)
#     scar_values.loc[column, 'scar[+0 +6]'] = sum(sar.loc[11:17, column]) / (len(sar.loc[11:17, column]) ** 0.5)
#     # 可自行新增窗格

# scar_ttest_result = round(scar_values.sum() / sigma_sar, 3)
# scar_ttest_result = pd.DataFrame(scar_ttest_result, columns=['scar_t_value'])

# scar_ttest_result['p_value'] = scar_ttest_result['scar_t_value'].apply(lambda x: 2 * stats.t.sf(abs(x), df = (21 - 2))) # 計算p value / df=事件期長度21天（21筆資料）再做自由度修正-2

# car_ttest_result = pd.DataFrame(car_ttest).set_index('Column')
# car_ttest_result['significance'] = car_ttest_result['p_value'].apply(label_p_value)

# scar_ttest_result['significance'] = scar_ttest_result['p_value'].apply(label_p_value)

# car_signtest_result = pd.DataFrame(car_signtest).set_index('Column')
# car_signtest_result['significance'] = car_signtest_result['p_value'].apply(label_p_value)

# car_signed_rank_result = pd.DataFrame(car_signed_rank).set_index('Column')
# car_signed_rank_result['significance'] = car_signed_rank_result['p_value'].apply(label_p_value)


# print('---------AR t test 按公式計算結果---------', '\n', ar_ttest_fml, '\n''\n')
# print('--------- AR t test 套件計算結果 ---------', '\n', ar_ttest_result, '\n''\n')
# print('--------- AR SRM t test 公式計算結果 ---------', '\n', ar_srm_ttest, '\n''\n')
# print('--------- AR sign test 公式計算結果 ---------', '\n', signtest_result, '\n''\n')
# print('--------- AR wilcoxon signed-rank test 套件計算結果 ---------', '\n', signed_rank_result, '\n''\n')

# print('---------CAR t test 套件計算結果---------', '\n', car_ttest_result, '\n''\n')
# print('---------CAR SRM t test 公式計算結果---------', '\n', scar_ttest_result, '\n''\n')
# print('---------CAR sign test 公式計算結果---------', '\n', car_signtest_result, '\n''\n')
# print('---------CAR wilcoxon signed-rank test 套件計算結果---------', '\n', car_signed_rank_result, '\n''\n')

# with pd.ExcelWriter('/Users/alex/Desktop/論文/我的論文/assay python code/Statistic test_result.xlsx', engine='openpyxl') as writer:
#     ar_ttest_fml.to_excel(writer, sheet_name='AR t test formula result', index=True)
#     ar_ttest_result.to_excel(writer, sheet_name='AR t test package result', index=True)
#     ar_srm_ttest.to_excel(writer, sheet_name='AR SRM t test', index=True)
#     signtest_result.to_excel(writer, sheet_name='AR sign test', index=True)
#     signed_rank_result.to_excel(writer, sheet_name='AR signed-rank test', index=True)
#     car_ttest_result.to_excel(writer, sheet_name='CAR t test package result', index=True)
#     scar_ttest_result.to_excel(writer, sheet_name='CAR SRM t test', index=True)
#     car_signtest_result.to_excel(writer, sheet_name='CAR sign test', index=True)
#     car_signed_rank_result.to_excel(writer, sheet_name='CAR signed-rank test', index=True)