#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import locale

#from market_watch.db import market_db

EL = "\n"
DEL = "\n\n"

def get_info(code):

    info = {}
    url = "http://services1.aastocks.com/web/cjsh/IndustrySection.aspx?CJSHLanguage=Chi&symbol=" + code

    print("URL: [" + url + "]")
    
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

    print(get_info('3993'))
 
if __name__ == "__main__":
    main()                
              



