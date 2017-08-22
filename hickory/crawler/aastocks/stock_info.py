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
    
def get_technical(code):

    info = {}
    url = "http://www.aastocks.com/en/stocks/analysis/company-fundamental/basic-information?symbol=" + code

    #print("URL: [" + url + "]")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
    sd =(code, )
    
    t1 = soup.find_all("table", {"class": "cnhk-cf"})[0]
    t2 = soup.find_all("table", {"class": "cnhk-cf"})[1]
    t3 = soup.find_all("table", {"class": "cnhk-cf"})[2]
  
    _1month_avg_vol = rf(t2.find_all("tr")[9].find_all("td")[1].text)
    _3month_avg_vol = rf(t2.find_all("tr")[10].find_all("td")[1].text)
    last_close = rf(t2.find_all("tr")[11].find_all("td")[1].text)

    _1month_avg_turnover = _3month_avg_turnover = 0
    
    if (last_close and _1month_avg_vol and _3month_avg_vol):
        _1month_avg_turnover = float(last_close) * float(_1month_avg_vol)
        _3month_avg_turnover = float(last_close) * float(_3month_avg_vol)
    
    # start with authorized_capital
    sd = (code,
          t1.find_all("tr")[0].find_all("td")[1].text.strip(),      #name
          rf(t1.find_all("tr")[8].find_all("td")[1].text),  #authorized_capital
          rf(t1.find_all("tr")[9].find_all("td")[1].text),  #issued_capital
          rf(t1.find_all("tr")[10].find_all("td")[1].text), #issued_capital_h
          rf(t1.find_all("tr")[12].find_all("td")[1].text), #nav
          rf(t1.find_all("tr")[13].find_all("td")[1].text), #eps
          rf(t1.find_all("tr")[14].find_all("td")[1].text), #pe
          rf(t1.find_all("tr")[15].find_all("td")[1].text), #dps
          rf(t1.find_all("tr")[16].find_all("td")[1].text), #yield
          rf(t1.find_all("tr")[17].find_all("td")[1].text), #pnav
          
          rf(t2.find_all("tr")[0].find_all("td")[1].text),  #_1month_change
          rf(t2.find_all("tr")[1].find_all("td")[1].text),  #_3month_change
          rf(t2.find_all("tr")[2].find_all("td")[1].text),  #_52week_change
          rf(t2.find_all("tr")[3].find_all("td")[1].text),  #_1month_hsi_relative
          rf(t2.find_all("tr")[4].find_all("td")[1].text),  #_3month_hsi_relative
          rf(t2.find_all("tr")[5].find_all("td")[1].text),  #_52week_hsi_relative
          rf(t2.find_all("tr")[6].find_all("td")[1].text),  #market_capital
          rf(t2.find_all("tr")[7].find_all("td")[1].text),  #_52week_high
          rf(t2.find_all("tr")[8].find_all("td")[1].text),  #_52week_low
          _1month_avg_vol,                                  #_1month_avg_vol
          _3month_avg_vol,                                  #_3month_avg_vol
          last_close,                                       #last_close
          _1month_avg_turnover,                             #_1month_avg_turnover
          _3month_avg_turnover,                             #_3month_avg_turnover
          rf(t3.find_all("tr")[0].find_all("td")[1].text),  #_10_day_ma
          rf(t3.find_all("tr")[1].find_all("td")[1].text),  #_50_day_ma
          rf(t3.find_all("tr")[2].find_all("td")[1].text),  #_90_day_ma
          rf(t3.find_all("tr")[3].find_all("td")[1].text),  #_250_day_ma
          rf(t3.find_all("tr")[4].find_all("td")[1].text),  #_14_day_rsi
    )
    #print(sd)
    return sd 
   

def get_info(code):

    info = {}
    url = "http://services1.aastocks.com/web/cjsh/IndustrySection.aspx?CJSHLanguage=Chi&symbol=" + code

    #print("URL: [" + url + "]")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
   
    data  = soup.find_all("script")[3].text
    industry_cd = data.split("'")[3]

    #print(industry_cd) 
    
    option = soup.find_all('option', {'value': industry_cd})[0]
    #print(option.text)

    td1 = soup.find_all('td', {'style': "font-weight:bold;"})[0]
    td2 = soup.find_all('td', {'style': "font-weight:bold;"})[1]
    #print(td.text)

    info["industry"] = option.text
    info["stockName"] = td1.text
    info["close"] = td2.text

    return info

def main():

    #print(get_info('3993'))
    print(get_technical('175'))
if __name__ == "__main__":
    main()                
              



