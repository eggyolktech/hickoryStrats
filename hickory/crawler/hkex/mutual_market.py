#!/usr/bin/python

from bs4 import BeautifulSoup
from decimal import Decimal
import requests
import sys
import re
import os
from datetime import date
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from hickory.db import stock_db
from hickory.util import file_util, date_util, stock_util
from hickory.report import mf_report

DATE_DESCS = ["0", "3", "7", "14", "30"]
EL = '\n'
DEL = '\n\n'

def generate_moneyflow_dump():

    dlist = date_util.get_wd_date_list(1, 30)
    #print(dlist)
    dates = [dlist[0], dlist[2], dlist[6], dlist[13], dlist[-1]]

    for index, date in enumerate(dates):
        shs_dict = get_shareholding(date)
        file_util.save_obj(shs_dict, DATE_DESCS[index])

def get_moneyflow_stocks():

    rlist = []
    rdict = file_util.load_obj(DATE_DESCS[0])

    if (rdict):
        for r in rdict:
            rlist.append(r['code'].zfill(5))
    
    return rlist

def get_moneyflow_map_by_code(code):

    rmap = {}
    code = code.lstrip("0")
    rdicts = []

    for desc in DATE_DESCS:
        try:
            rdicts.append(search_stock(code, file_util.load_obj(desc)))
        except:
            return rmap
    #print(rdicts)
    #print(code + str(rdicts[1]))
    if (rdicts[0] and rdicts[1] and rdicts[2] and rdicts[3]):
        r1 = rdicts[0][0]
        r3 = rdicts[1][0]
        r7 = rdicts[2][0]
        r14 = rdicts[3][0]
        #r30 = rdicts[4][0]

        rmap['code'] = code.zfill(5)
        rmap['shs'] = int(r1['shs'])
        rmap['stake'] = r1['percentage']
        rmap['3dshs'] = int(r3['shs'])
        rmap['7dshs'] = int(r7['shs'])
        rmap['14dshs'] = int(r14['shs'])
        rmap['3dshsg'] = (int(r1['shs']) - int(r3['shs']))/float(r3['shs']) * 100
        rmap['7dshsg'] = (int(r1['shs']) - int(r7['shs']))/float(r7['shs']) * 100
        rmap['14dshsg'] = (int(r1['shs']) - int(r14['shs']))/float(r14['shs']) * 100

    else:
        return rmap

    return rmap

def get_moneyflow_by_code(code):

    passage = ""
    code = code.lstrip("0")
    rdicts = []

    for desc in DATE_DESCS:
        try:
            rdicts.append(search_stock(code, file_util.load_obj(desc)))
        except:
            passage = "Moneyflow data not found!"
            return passage
    #print(rdicts)
    if (rdicts[0] and rdicts[1] and rdicts[2] and rdicts[3]):
        r1 = rdicts[0][0]
        r3 = rdicts[1][0]
        r7 = rdicts[2][0]
        r14 = rdicts[3][0]
        #r30 = rdicts[4][0]

        passage = "<b>" + code.zfill(5) + ".HK - " + stock_db.get_stock_name(code) + "</b> (" + stock_db.get_stock_industry(code) + ")" + DEL
        passage = passage + "Shares (Latest): " + stock_util.rf2s(int(r1['shs'])) + " / " + r1['percentage'] + EL
        passage = passage + "Shares (3 Days): " + stock_util.rf2s(int(r3['shs'])) + " / " + r3['percentage'] + EL
        passage = passage + "Shares (7 Days): " + stock_util.rf2s(int(r7['shs'])) + " / " + r7['percentage'] + EL
        passage = passage + "Shares (14 Days): " + stock_util.rf2s(int(r14['shs'])) + " / " + r14['percentage'] + EL
        #passage = passage + "Shares (30 Days): " + r30['shs'] + "/" + r30['percentage'] + EL

        passage = passage + EL
        passage = passage + "Growth (3 Days): " + stock_util.rfDeltaPercentage(r1['shs'], r3['shs']) + EL
        passage = passage + "Growth (7 Days): " + stock_util.rfDeltaPercentage(r1['shs'], r7['shs']) + EL
        passage = passage + "Growth (14 Days): " + stock_util.rfDeltaPercentage(r1['shs'], r14['shs']) + EL

        passage = passage + EL
        passage = passage + "Q: /qQ" + code + " C: /qd" + code + " N: /qn" + code + DEL
        passage = passage + "Last Updated: " + r1['date'] + EL 
    else:
        passage = "No Moneyflow data found for " + code
        return passage

    if (passage):
        passage = "<i>Southbound Moneyflow Trend for %s.HK</i>" % code.zfill(5) + DEL + passage
        return passage

def get_shareholding(sdate):

    DEL = "\n\n"
    EL = "\n"
    passage = ""

    dstr = sdate.strftime('%d')
    mstr = sdate.strftime('%m')
    ystr = sdate.strftime('%Y')
    print(dstr)
    print(mstr)
    print(ystr)   
    if (os.name == 'nt'):
        browser = webdriver.Chrome('C:\project\common\chromedriver.exe')
    else:
        browser = webdriver.PhantomJS() 
 
    browser.get(r'http://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=hk')

    select = Select(browser.find_element_by_id('ddlShareholdingMonth'))
    select.select_by_visible_text(mstr)
    
    select = Select(browser.find_element_by_id('ddlShareholdingDay'))
    select.select_by_visible_text(dstr)

    select = Select(browser.find_element_by_id('ddlShareholdingYear'))
    select.select_by_visible_text(ystr)

    #elemCode = browser.find_element_by_id('ddlShareholdingMonth')
    #elemCode.send_keys(mstr)

    #elemCode = browser.find_element_by_id('ddlShareholdingDay')
    #elemCode.send_keys(dstr)

    #elemCode = browser.find_element_by_id('ddlShareholdingYear')
    #elemCode.send_keys(ystr)
    
    elemSearch = browser.find_element_by_id('btnSearch')
    elemSearch.click()
   
    result = []
 
    # Detect if there is any alert
    try:
        alert = browser.switch_to_alert()
        error = alert.text
        print("error: " + error)
        alert.accept()
        print("alert accepted")
        browser.close()
        return result
    except:
        print("no alert")
    
    html = browser.page_source
    
    browser.close()

    soup = BeautifulSoup(html, "html.parser")
    #print(soup)
    resultTable = soup.find('table', {"class": "result-table"})
    
    if (resultTable):
        trows = resultTable.findAll("tr")[2:]

        for row in trows:
            cols = row.findAll("td")
            stk = {}
            stk['date'] = ystr + "-" + mstr + "-" + dstr
            stk['code'] = cols[0].text.strip().strip('\n')
            stk['shs'] = cols[2].text.replace(",","").strip().strip('\n')
            stk['percentage'] = cols[3].text.strip().strip('\n')

            if (stk['code'] == "136"):
                print(stk)
            result.append(stk)

    return result

def search_stock(code, stocklist):
    return [element for element in stocklist if element['code'] == code]

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def main(args):

    #print(get_shareholding(datetime.now().date()))
    if (len(args) > 1):
        if (args[1] == "gen_dump"):
            generate_moneyflow_dump()
            mf_report.generate()
    else:
        #print(get_moneyflow_by_code("1"))
        #print(get_moneyflow_by_code("2"))
        #print(get_moneyflow_by_code("1548"))
        #get_shareholding("20171103")
        print(get_moneyflow_by_code("136"))
        #print(get_moneyflow_by_code("6116"))
        #print(get_moneyflow_map_by_code("6116"))
        #print(get_moneyflow_stocks())
        print("OPTS: gen_dump")
   
if __name__ == "__main__":
    main(sys.argv)                
              



