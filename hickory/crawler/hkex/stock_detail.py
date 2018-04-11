#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import requests
from hickory.db import stock_db
from hickory.util import stock_util
from hickory.crawler.aastocks import stock_quote

import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def format_mkt_cap(_mktcaptxt):

    if "-" == _mktcaptxt:
        return "0"

    _mktcap = stock_util.rf(_mktcaptxt.replace("EUR","").replace("RMB","").replace("US","").replace("HK","").replace("$","").replace("*",""))
    if "US" in _mktcaptxt:
        _mktcap = "%.0f" % (_mktcap * 7.77)
    elif "RMB" in _mktcaptxt:
        _mktcap = "%.0f" % (_mktcap * 1.11)
    elif "EUR" in _mktcaptxt:
        _mktcap = "%.0f" % (_mktcap * 9.64)
    else:
        _mktcap = "%.0f" % _mktcap
    
    return _mktcap
 
def get_hkex_equ_dtl(code):

    _code = code.lstrip("0")
    
    url = "http://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=%s&sc_lang=zh-hk" % _code

    #print("URL: [" + url + "]")

    if (os.name == 'nt'):
    
        options = Options()  
        options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        browser = webdriver.Chrome(executable_path="C:\Wares\chromedriver.exe", chrome_options=options)  
    else:
        browser = webdriver.PhantomJS() 

    browser.implicitly_wait(3) # seconds
    browser.get(url)
    #print("Start dummy pass...") 
    try:
        myDynamicElement = browser.find_element_by_id("dummyid")
    except:
        pass
        
    html = browser.page_source   
    #print(html)
    browser.quit()
        
    soup = BeautifulSoup(html, "html.parser")
    
    _name = soup.find("div", {"class": "left_list_title"}).find("p", {"class": "col_name"}).text
    _name = _name.split()[0].strip()    
    _longname = soup.find("span", {"class": "col_longname"}).text.strip()
    _lotsize = soup.find("dt", {"class": "col_lotsize"}).text.replace(",","").strip()
    _industry = soup.find("span", {"class": "col_industry_hsic"}).text.strip()
    _mktcaptxt = soup.find("dt", {"class": "col_mktcap"}).text.strip()
    
    if ("H股" in _longname):
        _shsType = "H"
    else:
        _shsType = "N"    
    
    _cat = "CORP"
    _indLv1 = _industry.split("-")[0].strip()
    _indLv2 = _industry.split("-")[1].strip()
    
    if (len(_industry.split("-")) > 2):
        _indLv3 = _industry.split("-")[2].strip()
    else:
        _indLv3 = _indLv2

    _mktcap = format_mkt_cap(_mktcaptxt)       
    
    stock_db.manage_stock(_cat, code, _name, _indLv1, _indLv2, _indLv3, _lotsize, _mktcap, _shsType)   
    
    print("|".join([code,_name,_indLv1,_indLv2,_indLv3,_lotsize,_mktcap,_shsType]))
    

def get_hkex_etf_dtl(code):

    _code = code.lstrip("0")

    url = "http://www.hkex.com.hk/Market-Data/Securities-Prices/Exchange-Traded-Products/Exchange-Traded-Products-Quote?sym=%s&sc_lang=zh-hk" % _code

    #print("URL: [" + url + "]")

    if (os.name == 'nt'):
    
        options = Options()  
        options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        browser = webdriver.Chrome(executable_path="C:\Wares\chromedriver.exe", chrome_options=options)  
    else:
        browser = webdriver.PhantomJS() 

    browser.implicitly_wait(3) # seconds
    browser.get(url)
    #print("Start dummy pass...") 
    try:
        myDynamicElement = browser.find_element_by_id("dummyid")
    except:
        pass
        
    html = browser.page_source   
    #print(html)
    browser.quit()
        
    soup = BeautifulSoup(html, "html.parser")
    
    _name = soup.find("div", {"class": "left_list_title"}).find("p", {"class": "col_name"}).text
    _name = _name.split()[0].strip()    
    _longname = soup.find("span", {"class": "col_longname"}).text.strip()
    _lotsize = soup.find("dt", {"class": "col_lotsize"}).text.replace(",","").strip()
    _issuer = soup.find("td", {"class": "col_issuer"}).text.strip()
    _mktcaptxt = soup.find("dt", {"class": "col_aum"}).text.strip()
    
    if ("H股" in _longname):
        _shsType = "H"
    else:
        _shsType = "N"    
    
    _cat = "ETF"
    _indLv1 = _cat
    _indLv2 = _cat
    _indLv3 = _issuer
    
    _mktcap = format_mkt_cap(_mktcaptxt)       
    
    stock_db.manage_stock(_cat, code, _name, _indLv1, _indLv2, _indLv3, _lotsize, _mktcap, _shsType)   
    
    print("|".join([code,_name,_indLv1,_indLv2,_indLv3,_lotsize,_mktcap,_shsType]))
            
def get_hkex_reits_dtl(code):

    _code = code.lstrip("0")

    url = "http://www.hkex.com.hk/Market-Data/Securities-Prices/Real-Estate-Investment-Trusts/Real-Estate-Investment-Trusts-Quote?sym=%s&sc_lang=zh-hk" % _code

    #print("URL: [" + url + "]")

    if (os.name == 'nt'):
    
        options = Options()  
        options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        browser = webdriver.Chrome(executable_path="C:\Wares\chromedriver.exe", chrome_options=options)  
    else:
        browser = webdriver.PhantomJS() 

    browser.implicitly_wait(3) # seconds
    browser.get(url)
    #print("Start dummy pass...") 
    try:
        myDynamicElement = browser.find_element_by_id("dummyid")
    except:
        pass
        
    html = browser.page_source   
    #print(html)
    browser.quit()
        
    soup = BeautifulSoup(html, "html.parser")
    
    _name = soup.find("div", {"class": "left_list_title"}).find("p", {"class": "col_name"}).text
    _name = _name.split()[0].strip()    
    _longname = soup.find("div", {"class": "col_longname"}).text.strip()
    _lotsize = soup.find("dt", {"class": "col_lotsize"}).text.replace(",","").strip()
    _issuer = soup.find("span", {"class": "col_fund_manager"}).text.strip()
    _mktcaptxt = soup.find("dt", {"class": "col_mktcap"}).text.strip()
    
    if ("H股" in _longname):
        _shsType = "H"
    else:
        _shsType = "N"    
    
    _cat = "房地產投資信託基金"
    _indLv1 = _cat
    _indLv2 = _cat
    _indLv3 = _issuer
    
    _mktcap = format_mkt_cap(_mktcaptxt)       
            
    stock_db.manage_stock(_cat, code, _name, _indLv1, _indLv2, _indLv3, _lotsize, _mktcap, _shsType)   
    
    print("|".join([code,_name,_indLv1,_indLv2,_indLv3,_lotsize,_mktcap,_shsType]))
   

def main():

    #stock_db.init()

    #sync_equ_list()
    #sync_nonequ_list("ETF")
    #sync_nonequ_list("REIT")

    #sync_nonequ_list("INVP")
    #sync_nonequ_list("TRUST")
    #sync_equ_list("HDRS")
    #sync_equ_list("INVC")
    #sync_equ_list("GEMS")
    get_hkex_equ_dtl("00257")
    get_hkex_etf_dtl("02800")
    get_hkex_reits_dtl("00823")
    
    #get_hkex_equ_dtl("03988")
 
if __name__ == "__main__":
    main()                
              



