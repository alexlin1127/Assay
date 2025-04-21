"""

"""
import requests
from bs4 import BeautifulSoup
import csv

def main():
    firms = []
    output_path = '/Users/alex/Desktop/內生性新聞html'  # 變更路徑

    with open('/Users/alex/Desktop/news collecting & filter code/sp500 stock output.csv', newline='') as csvfile: # 這裡也要
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            firms.append(row[1])

    url = 'file:///Users/alex/Desktop/EBSCOhost%20檢索系統.html'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, features="html.parser")

    data = soup.find_all('div', class_="print-ft-content")
    count = 1236

    for news in data:
        all_text = news.get_text(separator="\n")
        lines = [line.strip() for line in all_text.splitlines() if line.strip()]

        content_words = " ".join(lines[1:]).split()

        if len(content_words) > 50:
            pass
        else:
            continue

        title = lines[0]
        following_text = " ".join(content_words[:25])
        search_area = title + " " + following_text

        if any(firm in search_area for firm in firms):
            with open(f"{output_path}/{count}.txt", "w", encoding="utf-8") as file:  
                file.write(all_text)
                count += 1
        else:
            continue

if __name__ == '__main__':
    main()
