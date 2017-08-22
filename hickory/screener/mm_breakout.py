#!/usr/bin/python
import numpy as np
import pandas as pd
import datetime
import configparser
import sys
import os
import urllib.request
import urllib.parse
import sqlite3
import locale
import concurrent.futures
import time
from datetime import tzinfo, timedelta, datetime
from hickory.util import config_loader, stock_util
from hickory.indicator import gwc
from hickory.data import webdata
from hickory.crawler.aastocks import stock_quote, stock_info
from hickory.db import stock_tech_db, stock_sector_db
#from hickory.report import sector_heatmap

config = config_loader.load()

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def manageStockInd(code):

    ycode = code.lstrip("0");

    if (is_number(ycode)):
        ycode = ycode.rjust(4, '0') + ".HK"
   
    end = datetime.today()
    start = end - timedelta(days=(3*30))

    bars = webdata.DataReader(ycode, "yahoo_direct", start, end)
    
    if (len(bars) == 0):
        return True

    bars['Volume'] = bars['Volume'].replace('null', 0)
    bars_trim = bars[:-1]
    bars_trim2 = bars[:-4]
    mean_vol = bars_trim['Volume'].mean()
    mclose = bars_trim['Close'].max()
    m2close = bars_trim2['Close'].max()
    minclose = bars_trim['Close'].min()
    #range_close = (max_close - min_close)/min_close

    di = bars.tail(1).iloc[0]
    dt = bars.tail(3).head(1).iloc[0]

    lclose = di['Close']
    l2close = dt['Close']
    rclose = (mclose - minclose)/l2close * 100
    
    if (mean_vol > 0):
        lvav = di['Volume']/mean_vol
    else:
        lvav = 0

    f = "%.2f"
    #print(code)
    if (lvav >= 3 and lclose > mclose and l2close < m2close):
        print("Code: [" + code + ", " + f % lvav + ", " + f % lclose + ", " + f % rclose + "%]")
     
    #if (mean_vol > 0 and di['Volume'] and di['Volume']/mean_vol >= 2 and di['Close'] > max_close):
        #print("Code: [" + code + "] Breakout Found with Range Close: [" + range_close + "]")
    

    #st = (code, f % di['sma30'], f % di['sma100'], f % di['sma150'], f % di['sma200'])
    #print(st)
    
    #result = stock_tech_db.manage_stock_tech(st, True)
    result = True
    return result

def generate_IND_MT(num_workers=1):

    conn = sqlite3.connect("/app/hickoryStrats/hickory/db/stock_db.dat")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("select * from stocks order by code asc")
    rows = c.fetchall()

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Start the load operations and mark each future with its URL
        future_to_manage = {executor.submit(manageStockInd, row["code"]): row for row in rows}
        
        for future in concurrent.futures.as_completed(future_to_manage):
            row = future_to_manage[future]
            try:
                data = future.result()
            except Exception as exc:
                printout = row["code"]
                #print('%r generated an exception: %s' % (row["code"], exc))
            else:
                if (data == False):
                    print('%r result is %s' % (row["code"], data))    

def main(args):

    start_time = time.time()
    NO_OF_WORKER = 3 

    webdata.init_cookies_and_crumb()
    
    if (len(args) > 1 and args[1] == "gen_ind"):
        generate_IND_MT(NO_OF_WORKER)
    else:
        print("OPTS: gen_ind")
        #print(manageStockTech("175"))

    print("Time elapsed: " + "%.3f" % (time.time() - start_time) + "s")

if __name__ == "__main__":
    main(sys.argv) 
