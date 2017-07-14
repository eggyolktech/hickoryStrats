#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import json

#from market_watch.db import 

def get_stock_json():

    url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdeqty_c.htm"

    print("URL: [" + url + "]")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    
    table = soup.find("table", {"class": "table_grey_border"})

    stock_list = []
    master_list = []
    master_data_dict = {}

    for tr in table.find_all("tr")[1:]:

        cols = tr.find_all("td")
        print(cols[0].text + " - " + cols[1].text)
        
        stock_dict = {}
        stock_dict["code"] = cols[0].text
        stock_dict["label"] = cols[1].text
        stock_list.append(stock_dict)

    master_data_dict["code"] = "ALL_HKEX"
    master_data_dict["label"] = "ALL Securities List"
    master_data_dict["list"] = stock_list

    master_list.append(master_data_dict)

    json_data = json.dumps(master_list)
    print(json_data)

    return json_data

def main():

    get_stock_json()

 
if __name__ == "__main__":
    main()                
              



