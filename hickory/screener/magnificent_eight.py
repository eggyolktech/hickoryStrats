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
from hickory.util import config_loader, stock_util, mem_util
from hickory.indicator import gwc
from hickory.data import webdata
from hickory.crawler.aastocks import stock_quote, stock_info
from hickory.db import stock_tech_db, stock_sector_db
from hickory.report import y8_report
import random

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
    randays = random.randint(1,20)
    start = end - timedelta(days=(1*400 + randays))
    bars = webdata.DataReader(ycode, "yahoo_direct", start, end)
    #print("start: " + str(start) + ", " + "end: " + str(end))
    signals = pd.DataFrame(index=bars.index)
    pd.options.mode.chained_assignment = None  # default='warn'

    signals['close'] = bars['Close']
    #bars['Volume'] = bars['Volume'].replace('null', 0)
    #signals['vol'] = bars['Volume']
    #signals['turnover'] = bars['Close'] * bars['Volume'].astype(float)
    #mean_turnover = signals['turnover'].mean()
 
    col = "Close"
    signals['sma30'] = gwc.SMA(bars, col, 30)
    signals['sma100'] = gwc.SMA(bars, col, 100)
    signals['sma150'] = gwc.SMA(bars, col, 150)
    signals['sma200'] = gwc.SMA(bars, col, 200)
    
    # calculate ROC
    firstclose = bars.iloc[0]['Close']
    lastclose = bars.iloc[-1]['Close']
    lb = len(bars)

    _3mclose = bars.iloc[lb-63]['Close'] if lb > 63 else firstclose
    _6mclose = bars.iloc[lb-126]['Close'] if lb > 126 else firstclose
    _9mclose = bars.iloc[lb-189]['Close'] if lb > 189 else firstclose
    _12mclose = bars.iloc[lb-252]['Close'] if lb > 252 else firstclose
    print(code + "-" + str(lastclose))
    print(code + "-" + str(lastclose/_3mclose), str(lastclose/_6mclose), str(lastclose/_9mclose), str(lastclose/_12mclose))

    roc_mark = (2*(lastclose/_3mclose)) + (lastclose/_6mclose) + (lastclose/_9mclose) + (lastclose/_12mclose)
    
    #print(len(bars))
    #print(len(signals))
    #print(signals.head(50))  
    df = signals.tail(1)
    di = df.iloc[0]
    f = "%.4f"
    st = (code, f % di['sma30'], f % di['sma100'], f % di['sma150'], f % di['sma200'], _3mclose, _6mclose, _9mclose, _12mclose, roc_mark)
    #print(st)
    
    result = stock_tech_db.manage_stock_tech(st, True)
    #result = True
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
                print('%r generated an exception: %s' % (row["code"], exc))
            else:
                if (data == False):
                    print('%r result is %s' % (row["code"], data))    

def main(args):

    mem_util.set_max_mem(50)
    start_time = time.time()
    NO_OF_WORKER = 3 

    webdata.init_cookies_and_crumb()
    
    if (len(args) > 1 and args[1] == "gen_ind"):
        generate_IND_MT(NO_OF_WORKER)
        y8_report.generate()    
    else:
        print("OPTS: gen_ind")
        for stock in ("00612", "01918", "00581"):
            print(manageStockInd(stock))

    print("Time elapsed: " + "%.3f" % (time.time() - start_time) + "s")

if __name__ == "__main__":
    main(sys.argv) 
