#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import locale
from hickory.util import stock_util

#from market_watch.db import market_db

EL = "\n"
DEL = "\n\n"

def rf(text):
    return stock_util.rf(text)
  
def get_info(code):

    info = {}
    url = "http://www.etnet.com.hk/www/tc/stocks/realtime/quote_super.php?code=%s" % code.lstrip("0")

    print("URL: [" + url + "]")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
   
    rows  = soup.find("div", {"id": "content"}).findAll("table")[2].find("tbody").findAll("tr")
   
    print(rows) 
    stk_month_high = rows[2].findAll("td")[1].text
    print("AAA%s " % stk_month_high)
    stk_volume = rows[2].findAll("td")[3].text
    stk_month_low = rows[3].findAll("td")[1].text
    stk_turnover = rows[3].findAll("td")[3].text      
    stk_week_high = rows[4].findAll("td")[1].text   
    stk_short_amount = rows[4].findAll("td")[3].text   
    stk_week_low = rows[5].findAll("td")[1].text   
    stk_ma_10 = rows[5].findAll("td")[3].text
    stk_ma_20 = rows[6].findAll("td")[3].text
    stk_ma_50 = rows[7].findAll("td")[3].text
    stk_ma_250 = rows[8].findAll("td")[3].text
    stk_rsi_14 = rows[9].findAll("td")[3].text
    stk_gain_10 = rows[10].findAll("td")[3].text

    ldict = locals()   

    for key in ldict:
        if ("stk_" in key):
            info[key] = ldict[key]

    return info

def main():

    print(get_info('3993'))
    
if __name__ == "__main__":
    main()                
              
    
