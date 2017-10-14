#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import locale
import re
from hickory.db import stock_exchange_db
from hickory.util import stock_util

EL = "\n"
DEL = "\n\n"
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_stock_ex_list(exchange):

    url = "https://finance.google.com/finance?q=%5B(exchange%20%3D%3D%20%22" + exchange.upper()+ "%22)%5D&restype=company&noIL=1&start=0&num=5000"

    print("URL: [" + url + "]")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html5lib")
    
    table = soup.find("table", {"class": "company_results"})
    print(table)

    print(len(table.findAll("tr")[1:]))
    for tr in table.findAll("tr")[1:]:

        cols =  tr.findAll("td")
        name = cols[0].text
        exchange = cols[1].text
        symbol = cols[2].text

        #if not "Inactive" in name:
        print(exchange + ":" + symbol + " - " + name) 

def main():

    get_stock_ex_list("NASDAQ")


if __name__ == "__main__":
    main()                
              



