#!/usr/bin/python

from bs4 import BeautifulSoup
from decimal import Decimal
import urllib.request
import urllib.parse
import requests
import re
import os
from datetime import date
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from hickory.db import stock_mag8_db

EL = "\n"
DEL = "\n\n"

def rf(text):
    return stock_util.rf(text)
  
def get_stocks_tech(codes):

    DEL = "\n\n"
    EL = "\n"
    
    if (os.name == 'nt'):
        options = Options()  
        options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
        options.add_argument('--disable-gpu')
        #options.add_argument('--headless')
        browser = webdriver.Chrome(executable_path="C:\Wares\chromedriver.exe", chrome_options=options)  
    else:
        browser = webdriver.PhantomJS() 

    url = "http://www.etnet.com.hk/www/tc/stocks/realtime/quote_super.php" 
    browser.get(url)  
    
    try:
        browser.implicitly_wait(3) # seconds
        myDynamicElement = browser.find_element_by_id("dummyid")
    except:
        pass
 
    for code in codes:
    
        input = browser.find_element_by_id("globalsearch")
        input.send_keys(code.lstrip("0"))
        input.send_keys(u'\ue007')
        info = {}

        try:
            WebDriverWait(browser, 3).until(EC.alert_is_present(), 'Waiting for alert timed out')
            alert = browser.switch_to_alert()
            error = alert.text
            alert.accept()
            print("alert accepted")
            #browser.close()
        except:
            # only parse page if no alert
            print("no alert")
            
            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")  
     
            rows  = soup.find("div", {"id": "content"}).findAll("table")[0].find("tbody").findAll("tr")
            stk_code = code.lstrip("0")
            stk_close = rows[2].findAll("td")[0].text.strip()
            
            rows  = soup.find("div", {"id": "content"}).findAll("table")[2].find("tbody").findAll("tr")
            stk_high = rows[0].findAll("td")[1].text.strip()
            stk_prev_close = rows[0].findAll("td")[3].text.strip()
            stk_low = rows[1].findAll("td")[1].text.strip()
            stk_open = rows[1].findAll("td")[3].text.strip()
            stk_1month_high = rows[2].findAll("td")[1].text.strip()
            stk_volume = rows[2].findAll("td")[3].text.strip()
            stk_1month_low = rows[3].findAll("td")[1].text.strip()
            stk_turnover = rows[3].findAll("td")[3].text.strip()
            stk_52week_high = rows[4].findAll("td")[1].text.strip()
            stk_short_amount = rows[4].findAll("td")[3].text.strip()   
            stk_52week_low = rows[5].findAll("td")[1].text.strip()   
            stk_10ma = rows[5].findAll("td")[3].text.strip()
            stk_20ma = rows[6].findAll("td")[3].text.strip()
            stk_50ma = rows[7].findAll("td")[3].text.strip()
            stk_250ma = rows[8].findAll("td")[3].text.strip()
            stk_14rsi = rows[9].findAll("td")[3].text.strip()
            stk_10gain = rows[10].findAll("td")[3].text.strip()

            ldict = locals()   

            for key in ldict:
                if ("stk_" in key):
                    info[key] = ldict[key]
                    
            
            print(info)

    

def main():

    codes_list = stock_mag8_db.get_mag8_stocks_list()[:20]:
    print(codes_list)
    print(get_stocks_tech(codes_list))
    
if __name__ == "__main__":
    main()                
              
    
