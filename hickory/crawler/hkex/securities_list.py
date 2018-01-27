#!/usr/bin/python

from bs4 import BeautifulSoup
from selenium import webdriver
import os
import requests
import json

#from market_watch.db import 

def get_stock_json():

    url = "https://finance.google.com.hk/finance?q=[(exchange%20%3D%3D%20%22HKG%22)]&restype=company&noIL=1&start=1&num=10000"
    print("URL: [" + url + "]")

    #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    #r = requests.get(url, headers=headers)
    #html = r.text
    if (os.name == 'nt'):
        browser = webdriver.Chrome('C:\project\common\chromedriver.exe')
    else:
        browser = webdriver.PhantomJS()

    browser.get(r'https://finance.google.com.hk/finance?q=[(exchange%20%3D%3D%20%22HKG%22)]&restype=company&noIL=1&start=1&num=10000')

   # Detect if there is any alert
    try:
        alert = browser.switch_to_alert()
        error = alert.text
        print("error: " + error)
        alert.accept()
        print("alert accepted")
        browser.close()
    except:
        print("no alert")

    html = browser.page_source

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", {"class": "gf-table company_results"})
    #print("table:")
    #print(table)
    stock_list = []
    master_list = []
    master_data_dict = {}

    for tr in table.find_all("tr")[1:]:

        cols = tr.find_all("td")
        if (not len(cols) == 8):
            continue
        
        print(cols[2].text.strip() + " - " + cols[0].text.strip())
        
        stock_dict = {}
        stock_dict["code"] = cols[2].text.strip()
        stock_dict["label"] = cols[0].text.strip()
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
              



