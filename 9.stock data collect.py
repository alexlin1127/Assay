"""

"""
import yfinance as yf
import pandas as pd

def main():
    event = pd.read_excel('/Users/alex/Desktop/0511assay data測試/event list.xlsx')['Ticker'].to_list() # 請修改讀取excel檔案路徑
    event1 = []

    # 刪除重複出現的公司
    for x in event:
        if x not in event1:
            event1.append(x)

    stock_data = pd.DataFrame()
    stock = []
    print(len(event1))
    # # Event period 2018/01/01 - 2023/12/31 // Stock data period 2017/01/01 - 2024/01/31

    # # 迭代每個事件對應公司，並抓取股價資料
    for i in event1:
        x = str(i)
        data = yf.Ticker(x).history(start='2016-12-30', end='2024-02-01').reset_index() #股價的起始和結束日，請根據自身研究調整
        if len(data.index) == 1782: # 先print一家公司看stock data period index有多少再把1782改成你跑出來的index值
            data = data[['Date', 'Close']]
            data['Date'] = pd.to_datetime(data['Date'])
            data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')

            data['Ret'] = round(((data['Close'] - data['Close'].shift(1)) / data['Close'].shift(1)), 4)
            data = data.drop(data.index[0])
            data = data.drop("Close", axis=1)
            data.insert(0, 'Ticker', x)
            stock_data = pd.concat([stock_data, data], ignore_index=True)
        
        else:
            stock.append(i)
            continue


    # 取得市場指數 S&P 500的代碼是^GSPC
    sp500 = yf.Ticker("^GSPC")
    sp500data = sp500.history(start="2016-12-30", end="2024-02-01").reset_index()
    if len(sp500data.index) == 1782:
        sp500data = sp500data[['Date','Close']]
        sp500data['Date'] = pd.to_datetime(sp500data['Date'])
        sp500data['Date'] = sp500data['Date'].dt.strftime('%Y-%m-%d')
        sp500data['MarketRet'] = round(((sp500data['Close'] - sp500data['Close'].shift(1)) / sp500data['Close'].shift(1)), 4)
        sp500data = sp500data.drop(sp500data.index[0]).drop('Close', axis=1)

    else:
        print('Date Error')

    print(sp500data, '\n', stock_data)
    sp500data.to_excel("/Users/alex/Desktop/0511assay data測試/sp500data test.xlsx", index=False, engine="openpyxl") # 請改為要儲存在自己電腦中的路徑
    stock_data.to_excel("/Users/alex/Desktop/0511assay data測試/stock data test.xlsx", index=False, engine="openpyxl") # 這個也要

if __name__ == "__main__":
    main()