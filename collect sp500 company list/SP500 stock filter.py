'''

'''
import requests
from bs4 import BeautifulSoup
import pandas as pd

def main():
    urls = ['https://www.moneydj.com/us/uslist/list0005/XLE', 'https://www.moneydj.com/us/uslist/list0005/XLB',
        'https://www.moneydj.com/us/uslist/list0005/XLF', 'https://www.moneydj.com/us/uslist/list0005/XLI', 
        'https://www.moneydj.com/us/uslist/list0005/XLK', 'https://www.moneydj.com/us/uslist/list0005/XLP', 
        'https://www.moneydj.com/us/uslist/list0005/XLU', 'https://www.moneydj.com/us/uslist/list0005/XLV', 
        'https://www.moneydj.com/us/uslist/list0005/XLY', 'https://www.moneydj.com/us/uslist/list0005/XLC', 
        'https://www.moneydj.com/us/uslist/list0005/XLRE']

    test = []
    for url in urls:
        content = requests.get(url)
        if content.status_code == 200:
            soup = BeautifulSoup(content.text, 'html.parser')

            stock_name = soup.findAll("td", attrs={"class": "col03"})
            # print(stock_name)
            
            for stock in stock_name:
                test.append(f'{stock.string}')
                # print(stock.string)

    # 刪除有遺漏值的公司，共15家
    delete_stock = ['Corteva', 'Dow', 'Berkshire Hathaway - Class B', 'Veralto', 
                    'Otis Worldwide', 'Carrier Global', 'Ingersoll Rand', 'Uber',
                    'Dayforce', "Brown-Forman Corp. CL 'B'", 'Kenvue', 'Constellation',
                    'Moderna', 'GE HealthCare', 'Airbnb']

    result = [x for x in test if x not in delete_stock]

    df = pd.DataFrame(result, columns=['Values'])


    df.to_excel('/Users/alex/Desktop/論文/我的論文/assay python code/sp500 stock output.xlsx', # 記得變更路徑
                 index=False, 
                 header=False)

if __name__ == '__main__':
    main()