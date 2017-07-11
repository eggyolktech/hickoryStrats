#!/usr/bin/python

from bs4 import BeautifulSoup
import requests

from market_watch.db import market_db

def get_stock_quote(code):


    url = "http://www.aastocks.com/en/mobile/Quote.aspx?symbol=" + code

    print("URL: [" + url + "]")
    
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")

    div_last = soup.find("div", {"class": "text_last"})
    print(div_last.text.strip())

    td_last = soup.find("td", {"class": "cell_last"})
    print(td_last.find_all("div")[2].find_all("span")[0].text)
    print(td_last.find_all("div")[2].find_all("span")[1].text)
    print(td_last.find_all("div")[3].text.strip())

    td_last = soup.find("td", {"class": "cell_last_height"})
    print(td_last.find_all("td")[2].find("span").text)
    print(td_last.find_all("td")[3].find("span").text)
    print(td_last.find_all("td")[4].find("span").text)
    #print(soup.find("div", {"class": "ctl00_cphContent_pQuoteDetail"}))
    rows = soup.find("div", {"id": "ctl00_cphContent_pQuoteDetail"}).find_all("table")[0].find_all("tr", recursive=False)

    print(rows[2].find_all("td")[0].find("span").text)
    print(rows[2].find_all("td")[1].find("span").text)
    print(rows[3].find_all("td")[0].find("span").text)
    print(rows[3].find_all("td")[1].find("span").text)
    print(rows[4].find_all("td")[0].find("span").text)
    print(rows[4].find_all("td")[1].find("span").text)
    print(rows[5].find_all("td")[0].find("span").text)
    print(rows[5].find_all("td")[1].find("span").text)

    div52 = soup.find("div", {"id": "ctl00_cphContent_p52Week"})
    print(div52.find("span").text)
    


        
    return quote_result

def main():

    get_stock_quote('87001')

 
if __name__ == "__main__":
    main()                
              



