import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import linregress
from scipy import stats
from scipy.stats import norm


# # 讀取 Excel 檔 (請將路徑改為你電腦中的檔案路徑)
stock_data = pd.read_excel(r"/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/stock data test.xlsx")
market_return = pd.read_excel(r"/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/sp500data test.xlsx")
data = pd.read_excel("/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/classification data.xlsx")


# 分類高污染和低污染事件
# high_pollution_event = data[data['high pollution'] == 1][['nid', 'Ticker', 'Eventdate']]
# low_pollution_event = data[data['high pollution'] == 0][['nid', 'Ticker', 'Eventdate']]

# high_pollution_event.set_index('nid', inplace=True)
# high_pollution_event.reset_index(drop=True, inplace=True)
# high_pollution_event.index = high_pollution_event.index + 1
# print(f'Sample sizes: {len(high_pollution_event)}')


# low_pollution_event.set_index('nid', inplace=True)
# low_pollution_event.reset_index(drop=True, inplace=True)
# low_pollution_event.index = low_pollution_event.index + 1
# print(f'Sample sizes: {len(low_pollution_event)}')

# print(high_pollution_event)
# print(low_pollution_event)


# # 分類 ESG rating 高低
# high_esg_score = data[data['ESG rating'] == 1][['nid', 'Ticker', 'Eventdate']]
# low_esg_score = data[data['ESG rating'] == 0][['nid', 'Ticker', 'Eventdate']]

# high_esg_score.set_index('nid', inplace=True)
# high_esg_score.reset_index(drop=True, inplace=True)
# high_esg_score.index = high_esg_score.index + 1
# print(f'Sample sizes: {len(high_esg_score)}')


# low_esg_score.set_index('nid', inplace=True)
# low_esg_score.reset_index(drop=True, inplace=True)
# low_esg_score.index = low_esg_score.index + 1
# print(f'Sample sizes: {len(low_esg_score)}')

# # COP 會議前後
after_cop = data[data['COP 26 conference'] == 1][['nid', 'Ticker', 'Eventdate']]
before_cop = data[data['COP 26 conference'] == 0][['nid', 'Ticker', 'Eventdate']]

# before_cop.set_index('nid', inplace=True)
# before_cop.reset_index(drop=True, inplace=True)
# before_cop.index = before_cop.index + 1
# print(f'Sample sizes: {len(before_cop.index)}')

after_cop.set_index('nid', inplace=True)
after_cop.reset_index(drop=True, inplace=True)
after_cop.index = after_cop.index + 1
print(f'Sample sizes: {len(after_cop.index)}')



# 變更 stock_data、market_return 索引值從1開始(原始值為0)
stock_data.index = stock_data.index + 1
market_return.index = market_return.index + 1
market_return['Date'] = pd.to_datetime(market_return['Date'])
stock_data['Date'] = pd.to_datetime(stock_data['Date'])

event_ret = pd.DataFrame()
sar = []
var_Si_total = 0


for i in range(1, len(after_cop.index)+1):
    
    # 抓取事件日期
    event_date = datetime.strptime((after_cop.loc[after_cop.index[i - 1], 'Eventdate']), "%Y-%m-%d")

    # 抓取公司 Ticker
    ticker = after_cop.loc[after_cop.index[i - 1], 'Ticker']

    # 在 stock_data 中抓取該公司的股價資料
    ticker_i = pd.DataFrame(stock_data.loc[stock_data['Ticker'] == ticker, ['Ticker', 'Date', 'Ret']])
    ticker_i['Date'] = pd.to_datetime(ticker_i['Date'])
    ticker_i.reset_index(drop=True, inplace=True)
    ticker_i.index = ticker_i.index + 1
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


### 公式計算 AR t test ###
n = len(after_cop.index)
sigma_ar = (var_Si_total ** 0.5) / n

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
    test_data = pd.DataFrame(row.tolist(), columns=['test_data'], index=range(1, len(after_cop.index) + 1))
    test_data['test_data'] = pd.to_numeric(test_data['test_data'])
    
    ### 套件計算 AR t test ###
    t, p_value = stats.ttest_1samp(test_data, 0)
    ar_ttest_results.append({'t_value': t[0], 'p_value': p_value[0]})


### 公式計算 AR SRM t test ###
sar = pd.DataFrame(sar)
sar_result = []

for column in sar:
    test1 = sum(sar[column])
    Ti = 200 #估計其天數
    sigma_sar = (((Ti - 2) / (Ti - 4)) * n) ** 0.5
    sar_t = test1 / sigma_sar
    sar_result.append(sar_t)

### 套件計算 CAR t-test ###
car_values = pd.DataFrame()
for column in event_ret.columns:

    # # 檢測事件日之前，股價提前反映的情況，每個窗格間隔兩天為一單位
    # car_values.loc[column, 'car[-6 +0]'] = event_ret.loc[ 5:11, column].mean()  
    # car_values.loc[column, 'car[-4 +0]'] = event_ret.loc[ 7:11, column].mean()
    # car_values.loc[column, 'car[-2 +0]'] = event_ret.loc[ 9:11, column].mean()

    # 檢測事件日前後1-3天
    car_values.loc[column, 'car[-1 +1]'] = event_ret.loc[10:12, column].mean()  
    car_values.loc[column, 'car[-2 +2]'] = event_ret.loc[ 9:13, column].mean()  
    car_values.loc[column, 'car[-3 +3]'] = event_ret.loc[ 8:14, column].mean()

    car_values.loc[column, 'car[-4 +4]'] = event_ret.loc[ 7:15, column].mean()
    car_values.loc[column, 'car[-5 +5]'] = event_ret.loc[ 6:16, column].mean()
    car_values.loc[column, 'car[-10 +10]'] = event_ret.loc[ :, column].mean()

    # # 檢測事件日之後，股價才開始反應的情況，每個窗格間隔兩天為一單位
    # car_values.loc[column, 'car[+0 +2]'] = event_ret.loc[ 11:13, column].mean()
    # car_values.loc[column, 'car[+0 +4]'] = event_ret.loc[ 11:15, column].mean()  
    # car_values.loc[column, 'car[+0 +6]'] = event_ret.loc[ 11:17, column].mean()  
    # 可自行新增事件窗格

car_ave = pd.DataFrame(columns=['CAR ave', 'CAR median'])
car_ave['CAR ave'] =round(car_values.mean(axis=0) * 100, 3)
car_ave['CAR median'] = round(car_values.median(axis=0) * 100, 3)
# car_ave.to_excel('/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/分類data/car ave/after_cop car_ave.xlsx', index=True, engine='openpyxl')
print(car_ave)

car_ttest = []
car_signed_rank = []
car_signtest = []

for column in car_values.columns:

    ### 套件計算 CAR t test ###
    t_value, p_value4 = stats.ttest_1samp(car_values[column], 0)
    car_ttest.append({'Column': column, 't_value': round(t_value, 3), 'p_value': round(p_value4, 3)})

    ### 套件計算 CAR signed-rank test ###
    sr, p_value5 = stats.wilcoxon(car_values[column] - 0, zero_method = "wilcox", alternative = "two-sided")
    car_signed_rank.append({'Column' : column, 'SR' : round(sr, 3), 'p_value' : round(p_value5, 3)})

    ### 公式計算 CAR sign test ###
    count1 = 0
    for x in car_values[column]:
        if x > 0 : 
            count1 += 1

    s1 = max(count1, n - count1) # 取n筆累計異常報酬中，正、負個數總合較大者（n=事件數150）
    mu1 = n * 0.5
    sigma1 = (n ** 0.5) * 0.5

    # 計算 z_score 和 p_values，並判斷顯著性
    z_score1 = [round((s1 - mu1 ) / sigma1, 3)]
    p_value6 = [round(2 * (1 - stats.norm.cdf(z)), 3) for z in z_score1]

    car_signtest.append({'Column' : column, "z_score" : z_score1[0], 'p_value' : p_value6[0]})

sar = pd.DataFrame(sar).T
scar_values = pd.DataFrame()

for column in sar.columns:

    # # 檢測事件日之前，股價提前反映的情況，每個窗格間隔兩天為一單位
    # scar_values.loc[column, 'scar[-6 +0]'] = sum(sar.loc[ 5:11, column]) / (len(sar.loc[ 5:11, column]) ** 0.5)
    # scar_values.loc[column, 'scar[-4 +0]'] = sum(sar.loc[ 7:11, column]) / (len(sar.loc[ 7:11, column]) ** 0.5)
    # scar_values.loc[column, 'scar[-2 +0]'] = sum(sar.loc[ 9:11, column]) / (len(sar.loc[ 9:11, column]) ** 0.5)

    # 檢測事件日前後1-3天
    scar_values.loc[column, 'scar[-1 +1]'] = sum(sar.loc[10:12, column]) / (len(sar.loc[10:12, column]) ** 0.5)
    scar_values.loc[column, 'scar[-2 +2]'] = sum(sar.loc[ 9:13, column]) / (len(sar.loc[ 9:13, column]) ** 0.5)
    scar_values.loc[column, 'scar[-3 +3]'] = sum(sar.loc[ 8:14, column]) / (len(sar.loc[ 8:14, column]) ** 0.5)
    
    scar_values.loc[column, 'scar[-4 +4]'] = sum(sar.loc[ 7:15, column]) / (len(sar.loc[ 7:15, column]) ** 0.5)
    scar_values.loc[column, 'scar[-5 +5]'] = sum(sar.loc[ 6:16, column]) / (len(sar.loc[ 6:16, column]) ** 0.5)
    scar_values.loc[column, 'scar[-10 +10]'] = sum(sar.loc[:, column]) / (len(sar.loc[ :, column]) ** 0.5)

    # # 檢測事件日之後，股價才開始反應的情況，每個窗格間隔兩天為一單位
    # scar_values.loc[column, 'scar[+0 +2]'] = sum(sar.loc[11:13, column]) / (len(sar.loc[11:13, column]) ** 0.5)
    # scar_values.loc[column, 'scar[+0 +4]'] = sum(sar.loc[11:15, column]) / (len(sar.loc[11:15, column]) ** 0.5)
    # scar_values.loc[column, 'scar[+0 +6]'] = sum(sar.loc[11:17, column]) / (len(sar.loc[11:17, column]) ** 0.5)
    # 可自行新增窗格

scar_ttest_result = scar_values.sum() / sigma_sar
scar_ttest_result = pd.DataFrame(round(scar_ttest_result, 3), columns=['scar_t_value'])

scar_ttest_result['p_value'] = scar_ttest_result['scar_t_value'].apply(lambda x: 2 * stats.t.sf(abs(x), df = (21 - 2))) # 計算p value / df=事件期長度21天（21筆資料）再做自由度修正-2

car_ttest_result = pd.DataFrame(car_ttest).set_index('Column')
car_ttest_result['significance'] = car_ttest_result['p_value'].apply(label_p_value)

scar_ttest_result['significance'] = scar_ttest_result['p_value'].apply(label_p_value)

car_signtest_result = pd.DataFrame(car_signtest).set_index('Column')
car_signtest_result['significance'] = car_signtest_result['p_value'].apply(label_p_value)

car_signed_rank_result = pd.DataFrame(car_signed_rank).set_index('Column')
car_signed_rank_result['significance'] = car_signed_rank_result['p_value'].apply(label_p_value)

# print("分析結果：事件公司所屬產業為高污染產業")
# print("分析結果：事件公司所屬產業為低污染產業")

# print("分析結果：MSCI ESG rating 屬於 Leader level")
# print("分析結果：MSCI ESG rating 非 Leader level")

# print("分析結果：事件日於COP會議之前")
# print("分析結果：事件日於COP會議之後")



print('---------CAR t test 套件計算結果---------', '\n', car_ttest_result, '\n''\n')
print('---------CAR SRM t test 公式計算結果---------', '\n', scar_ttest_result, '\n''\n')
print('---------CAR sign test 公式計算結果---------', '\n', car_signtest_result, '\n''\n')
print('---------CAR wilcoxon signed-rank test 套件計算結果---------', '\n', car_signed_rank_result, '\n''\n')

# with pd.ExcelWriter('/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/分類data/test result/after_cop.xlsx', engine='openpyxl') as writer:
#     car_ttest_result.to_excel(writer, sheet_name='CAR t test package result', index=True)
#     scar_ttest_result.to_excel(writer, sheet_name='CAR SRM t test', index=True)
#     car_signtest_result.to_excel(writer, sheet_name='CAR sign test', index=True)
#     car_signed_rank_result.to_excel(writer, sheet_name='CAR signed-rank test', index=True)