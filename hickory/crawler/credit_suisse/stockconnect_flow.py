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
    
def get_stock_connect_top_dict():

    top_inflow = {}
    top_outflow = {}

    for display in ["shares", "moneyflow"]:

        url = "http://warrants-hk.credit-suisse.com/en/stockconnect_moneyflow_popup_e.cgi?ucode=all&display=%s&order=2&desc=1" % (display)

        print("URL: [" + url + "]")
    
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        r = requests.get(url, headers=headers)
        html = r.text 
        #print(html)
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("div", {"class": "cnhk_connect_table"}).find("table")   
    
        inflow_rows = table.find("tbody").findAll("tr")[0:30]
        outflow_rows = table.find("tbody").findAll("tr")[-20:]
        print(len(inflow_rows))
        print(len(outflow_rows))
        for row in inflow_rows:
            #print(">>>" + str(row))
            code = row.findAll("td")[0].text.split("(")[1].replace(")","").zfill(5)
            value = row.findAll("td")[2].text
            top_inflow[code] = value

        for row in outflow_rows:
            #print("###" + str(row))
            code = row.findAll("td")[0].text.split("(")[1].replace(")","").zfill(5)
            value = row.findAll("td")[2].text
            top_outflow[code] = value
        
    return [top_inflow, top_outflow]

def main():

    dicts = get_stock_connect_top_dict()
    print(dicts[0])
    print(dicts[1])
    
if __name__ == "__main__":
    main()                
              



