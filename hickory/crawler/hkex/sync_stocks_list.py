#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import requests
from hickory.db import stock_db
from hickory.crawler.aastocks import stock_quote

#from market_watch.db import 

def sync_equ_list(cat="EQU"):

    if (cat == "EQU"):
        url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdeqty_c.htm"
    elif (cat == "HDRS"):
        url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdhdr_c.htm"
    elif (cat == "INVC"):
        url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdic_c.htm"
    elif (cat == "GEMS"):
        url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdgems_c.htm"
 
    print("URL: [" + url + "]")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    r.encoding = "UTF-8"
    html = r.text
   
    #soup = BeautifulSoup(html, "html.parser")
    soup = BeautifulSoup(html, "html5lib")
    
    table = soup.find("table", {"class": "table_grey_border"})

    stock_list = []
    master_list = []
    master_data_dict = {}
    _cat = "CORP"

    for tr in table.find_all("tr")[1:]:

        cols = tr.find_all("td")
        _code = (cols[0].text)
        _name = (cols[1].text)
        _lotsize = (cols[2].text.replace(",",""))
        a = cols[1].find("a")
        #print(_code)
         
        if (a):
            url_dtl = a["href"].replace("../../../", "http://www.hkex.com.hk/chi/")
            r_dtl = requests.get(url_dtl, headers=headers)
            r_dtl.encoding = "big5-hkscs"
            html_dtl = r_dtl.text
            soup_dtl = BeautifulSoup(html_dtl, "html5lib")
           
            table_dtl = soup_dtl.findAll("table")[5]
            nameTd = table_dtl.findAll("td", text=re.compile("證券名稱:"))
            name = nameTd[0].parent.findAll("td")[1].text.strip()

            if ("H股" in name):
                _shsType = "H"
            else:
                _shsType = "N"

            industryTd = table_dtl.findAll("td", text=re.compile("行業分類:"))
            #print(industryTd)
            industry = industryTd[0].parent.findAll("td")[1].text.strip().split("(")[0]
            _indLv1 = industry.split("-")[0].strip()
            _indLv2 = industry.split("-")[1].strip()
            
            if (len(industry.split("-")) > 2):
                _indLv3 = industry.split("-")[2].strip()
            else:
                _indLv3 = _indLv2
            
            mktCapTd = None
            mktCapTd = table_dtl.findAll("td", text=re.compile("市值"))

            if (not mktCapTd):
                t = {"bgcolor":"#99CCFF", "colspan":"0", "valign":"top", "align":"left", "height":"18", "width":"150"}
                tdList = table_dtl.findAll("td", t)
                for mtd in tdList:
                    if("市值" in mtd.text):
                        mktCapTd = [mtd]
                        break
            #print(mktCapTd)
            mktcaptxt = mktCapTd[0].parent.findAll("td")[1].text.strip()
            if (not mktcaptxt == "N/A"):         
                _mktcap = mktcaptxt.split(" ")[1].replace(",","")
            else:
                _mktcap = mktcaptxt
            
            #_mktcap = (table_dtl.findAll("tr")[15].findAll("td")[1].text.strip()).split(" ")[1].replace(",","")
            
            print(_code + " - " + _name + " - " +  _indLv3 + " - " + _lotsize + " - " + _mktcap + " - " + _shsType)
            stock_db.manage_stock(_cat, _code, _name, _indLv1, _indLv2, _indLv3, _lotsize, _mktcap, _shsType)

def sync_nonequ_list(cat):

    if (cat == "ETF"):
        url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdetf_c.htm"
    elif (cat == "REIT"):
        url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdreit_c.htm"
    elif (cat == "INVP"):
        url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/liproducts_c.htm"
    elif (cat == "TRUST"):
        url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdtrus_c.htm"
    else:
        return

    print("URL: [" + url + "]")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    r.encoding = "UTF-8"
    html = r.text
   
    #soup = BeautifulSoup(html, "html.parser")
    soup = BeautifulSoup(html, "html5lib")
    
    table = soup.find("table", {"class": "table_grey_border"})

    stock_list = []
    master_list = []
    master_data_dict = {}
    _cat = cat

    for tr in table.find_all("tr")[1:]:

        cols = tr.find_all("td")
        _code = (cols[0].text)
        _name = (cols[1].text)
        _lotsize = (cols[2].text.replace(",",""))
        _trust = cols[3].text
        a = cols[1].find("a")
        #print(_code)
         
        if (a):
            url_dtl = a["href"].replace("../../../", "http://www.hkex.com.hk/chi/")
            r_dtl = requests.get(url_dtl, headers=headers)
            r_dtl.encoding = "big5-hkscs"
            html_dtl = r_dtl.text
            soup_dtl = BeautifulSoup(html_dtl, "html5lib")
            
            table_dtl = soup_dtl.findAll("table")[5]
            #print(table_dtl)   
            _indLv1 = _cat
            _indLv2 = _cat
            _indLv3 = _trust
             
            for td in table_dtl.findAll("td"):
                
                if ("已發行基金單位" in td.text):
                    mktcaptxt = td.parent.findAll("td")[1].text.strip()

                    if (not mktcaptxt == "N/A"):
                        _mktcap = mktcaptxt.split("(")[0].replace(",","")
                        stock_obj = stock_quote.get_stock_quote(_code)
                        #print(_mktcap + " - " + stock_obj["Close"])
                        if (not stock_obj["Close"] == "N/A"):
                            _mktcap = int(_mktcap) * float(stock_obj["Close"])
                    else:
                        _mktcap = mktcaptxt
                    
                    break
            
            print(_code + " - " + _name + " - " +  _indLv3 + " - " + _lotsize + " - " + str(_mktcap))
            stock_db.manage_stock(_cat, _code, _name, _indLv1, _indLv2, _indLv3, _lotsize, _mktcap)

def main():

    #stock_db.init()

    sync_equ_list()
    #sync_nonequ_list("ETF")
    #sync_nonequ_list("REIT")

    #sync_nonequ_list("INVP")
    #sync_nonequ_list("TRUST")
    sync_equ_list("HDRS")
    sync_equ_list("INVC")
    sync_equ_list("GEMS")
 
if __name__ == "__main__":
    main()                
              



