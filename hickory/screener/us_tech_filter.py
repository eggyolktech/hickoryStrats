#!/usr/bin/python
import numpy as np
import pandas as pd
import configparser
import sys
import os
import urllib.request
import urllib.parse
import requests
import sqlite3
import locale
import concurrent.futures
import time
from datetime import tzinfo, timedelta, datetime
from hickory.util import config_loader, stock_util
from hickory.crawler.iextrading import stock_quote 
from hickory.db import stock_us_tech_db, stock_us_sector_db, stock_us_mag8_db
from hickory.report import sector_us_heatmap, y8_report, v8_report
from hickory.indicator import gwc
from hickory.data import webdata

if (not os.name == 'nt'):
    from hickory.util import mem_util

import random
import traceback
import logging

LIMIT = 7000 

#logging.basicConfig(filename='../log/manageUSStockTech.log',level=logging.WARNING)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

config = config_loader.load()

def get_stock_quote(code):

    qr = stock_quote.get_us_stock_quote(code)
    #print(qr)

    return qr

def manageStockTech(code, idm):

    #if (not code == "OPNT"):
    #    return True
    
    qr = get_stock_quote(code)

    if not qr:
        print("Stock Quote Not Found for [%s]" % code)
        return False

    # get tech info
    end = datetime.today()
    randays = random.randint(1,20)
    start = end - timedelta(days=(1*400 + randays))
    print("Code: [" + code + "]")
    bars = webdata.DataReader(code, "yahoo_direct", start, end)
    #print(code + " ---------- " + str(bars))

    #print("start: " + str(start) + ", " + "end: " + str(end))
    signals = pd.DataFrame(index=bars.index)
    pd.options.mode.chained_assignment = None  # default='warn'

    signals['close'] = bars['Close']
    bars['Volume'].fillna(0, inplace=True)
    #bars['Volume'] = bars['Volume'].replace('null', 0)
    signals['vol'] = bars['Volume']
    signals['turnover'] = bars['Close'] * bars['Volume'].astype(float)

    col = "Close"
    signals['sma10'] = gwc.SMA(bars, col, 10)
    signals['sma30'] = gwc.SMA(bars, col, 30)
    signals['sma50'] = gwc.SMA(bars, col, 50)
    signals['sma90'] = gwc.SMA(bars, col, 90)
    signals['sma100'] = gwc.SMA(bars, col, 100)
    signals['sma150'] = gwc.SMA(bars, col, 150)
    signals['sma200'] = gwc.SMA(bars, col, 200)
    signals['sma250'] = gwc.SMA(bars, col, 250)
    signals['vol30'] = gwc.SMA(bars, 'Volume', 30)
    signals['vol90'] = gwc.SMA(bars, 'Volume', 90)
    signals['to30'] = gwc.SMA(signals, 'turnover', 30)
    signals['to90'] = gwc.SMA(signals, 'turnover', 90)
    
    # calculate ROC
    firstclose = bars.iloc[0]['Close']
    lastclose = bars.iloc[-1]['Close']
    lb = len(bars)

    #print(bars)

    _1mth_close = bars.iloc[lb-21]['Close'] if lb > 21 else firstclose
    _3mth_close = bars.iloc[lb-63]['Close'] if lb > 63 else firstclose
    _6mth_close = bars.iloc[lb-126]['Close'] if lb > 126 else firstclose
    _9mth_close = bars.iloc[lb-189]['Close'] if lb > 189 else firstclose
    _12mth_close = bars.iloc[lb-252]['Close'] if lb > 252 else firstclose
    y8_roc_mark = (2*(lastclose/_3mth_close)) + (lastclose/_6mth_close) + (lastclose/_9mth_close) + (lastclose/_12mth_close)

    _1mth_change = ((lastclose - _1mth_close) / _1mth_close) * 100
    _3mth_change = ((lastclose - _3mth_close) / _3mth_close) * 100
    _52week_change = ((lastclose - _12mth_close) / _12mth_close) * 100

    #print([lastclose, _1mth_close])
    #print([lastclose, _3mth_close])
    #print([lastclose, _12mth_close])
    #print([_1mth_change, _3mth_change, _52week_change])

    _1mth_idx_change = idm[0]
    _3mth_idx_change = idm[1]
    _52week_idx_change = idm[2]

    _1mth_hsi_relative = (_1mth_change - _1mth_idx_change)
    _3mth_hsi_relative = (_3mth_change - _3mth_idx_change)
    _52week_hsi_relative = (_52week_change - _52week_idx_change)

    mktCap = stock_util.rf(qr["MktCap"])
    print("======= %s" % qr["MktCap"])
    print(mktCap)  
    df = signals.tail(1)
    latest = df.iloc[0]
    f = "%.4f"

    _1mth_avg_vol = latest['vol30']
    _3mth_avg_vol = latest['vol90']

    #print(_1mth_avg_vol)
    #print(_3mth_avg_vol)

    _1mth_avg_to = latest['to30']
    _3mth_avg_to = latest['to90']

    div = qr["DivRatio"] if "DivRatio" in qr else None
    syield = qr["Yield"] if "Yield" in qr else None
    eps = qr["EPS"] if "EPS" in qr else None
    pe = qr["PE"] if "PE" in qr else None
    wkLow = qr["52WeekLow"]
    wkHigh = qr["52WeekHigh"]
    
    st = (code,
          eps,
          pe,
          div,
          syield,
          _1mth_change,
          _3mth_change,
          _52week_change,
          _1mth_hsi_relative,
          _3mth_hsi_relative,
          _52week_hsi_relative,
          mktCap,
          wkHigh,
          wkLow,
          _1mth_avg_vol,
          _3mth_avg_vol, 
          qr["Close"],
          _1mth_avg_to,
          _3mth_avg_to,
          latest['sma10'],
          latest['sma50'],
          latest['sma90'],
          latest['sma250'],
          latest['sma30'],
          latest['sma100'],
          latest['sma150'],
          latest['sma200'],
          _3mth_close,
          _6mth_close,
          _9mth_close,
          _12mth_close,
          y8_roc_mark
         )

    result = stock_us_tech_db.manage_stock_tech(st)
    return result

def get_index_metrics():

    end = datetime.today()
    randays = random.randint(1,20)
    start = end - timedelta(days=(1*400 + randays))
    ycode = "%5EGSPC"
    bars = webdata.DataReader(ycode, "yahoo_direct", start, end)
    #print(bars)

    firstclose = bars.iloc[0]['Close']
    lastclose = bars.iloc[-1]['Close']
    lb = len(bars)

    _1mclose = bars.iloc[lb-21]['Close'] if lb > 21 else firstclose
    _3mclose = bars.iloc[lb-63]['Close'] if lb > 63 else firstclose
    _12mclose = bars.iloc[lb-252]['Close'] if lb > 252 else firstclose

    _1mchange = ((lastclose - _1mclose) / _1mclose) * 100
    _3mchange = ((lastclose - _3mclose) / _3mclose) * 100
    _12mchange = ((lastclose - _12mclose) / _12mclose) * 100

    return [_1mchange, _3mchange, _12mchange]

def generate_TECH_MT(num_workers=1):

    if (not os.name == 'nt'):
        dbfile = "/app/hickoryStrats/hickory/db/stock_us_db.dat"
    else:
        dbfile = "C:\\Users\\Hin\\eggyolktech\\hickoryStrats\\hickory\\db\\stock_us_db.dat"

    conn = sqlite3.connect(dbfile)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("select * from stocks_us order by code asc")
    rows = c.fetchall()
    idm = get_index_metrics()   
    #webdata.reset_cookies_and_crumb()

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Start the load operations and mark each future with its URL
        future_to_manage = {executor.submit(manageStockTech, row["code"], idm): row for row in rows[:LIMIT]}
        
        for future in concurrent.futures.as_completed(future_to_manage):
            row = future_to_manage[future]
            try:
                data = future.result()
            except ValueError:
                print("Data retrieving Error: " + row["code"])
                pass
            except Exception as exc:
                print('%r generated an exception: %s' % (row["code"], exc))
                print("Error retrieving code: " + row["code"])
                print(traceback.format_exc())
            else:
                if (data == False):
                    print('%r result is %s' % (row["code"], data))    

def manageStockVol(code):
    
    st = get_stock_quote(code)
    if (st):
        print(code + " - " + str(st["Close"]) + "/" + str(st["ChangePercent"]) + "/" +  str(st["Volume"]))
        result = stock_us_tech_db.update_stock_vol(code, st["Close"], st["ChangePercent"], stock_util.rf(st["Volume"]))
        return result
    else:
        print(code + " - Quote not found....!")
        return False


def generate_VOL_MT(stocks, num_workers=1):

    #print(stocks)

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Start the load operations and mark each future with its URL
        future_to_manage = {executor.submit(manageStockVol, code): code for code in stocks}
        
        for future in concurrent.futures.as_completed(future_to_manage):
            code = future_to_manage[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (code, exc))
                logging.error(" Error retrieving code: " + code)
                logging.error(traceback.format_exc())
            else:
                if (data == False):
                    print('%r result is %s' % (code, data))    

def main(args):

    if (not os.name == 'nt'):
        mem_util.set_max_mem(50)
    start_time = time.time()
    NO_OF_WORKER = 4 

    if (len(args) > 1 and args[1] == "gen_tech"):
        generate_TECH_MT(NO_OF_WORKER)
    elif (len(args) > 1 and args[1] == "gen_vol"):
        #for period in ["1m", "3m", "1y"]:
        generate_VOL_MT(stock_us_sector_db.get_hot_stocks_code("ALL"), NO_OF_WORKER-1)
        sector_us_heatmap.generate() 
        generate_VOL_MT(stock_us_mag8_db.get_mag8_stocks_list(), NO_OF_WORKER-1)
        y8_report.generate("US")    
    elif (len(args) > 1 and args[1] == "gen_all_vol"):
        generate_VOL_MT(stock_us_tech_db.get_all_stocks_code(), NO_OF_WORKER-1)
        v8_report.generate("US")
    else:
        print("OPTS: gen_tech | gen_vol | gen_all_vol")
        idm = get_index_metrics()
        #print(get_stock_quote("AAPL"))
        #print(get_us_stock_mktcap("AAPL"))
        #print(get_us_stock_mktcap("JPM"))
        print(manageStockTech("WMAR", idm))
        #print(manageStockVol("612"))

    #generate()
    print("Time elapsed: " + "%.3f" % (time.time() - start_time) + "s")

if __name__ == "__main__":
    main(sys.argv) 
