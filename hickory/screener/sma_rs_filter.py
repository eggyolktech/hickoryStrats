#!/usr/bin/python

import configparser
import sys
import os
import urllib.request
import urllib.parse
import sqlite3
import locale
import concurrent.futures
import time

from hickory.util import config_loader, stock_util
from hickory.crawler.aastocks import stock_quote, stock_info
from hickory.db import stock_tech_db, stock_sector_db
from hickory.report import sector_heatmap

config = config_loader.load()

def generate():

    conn = sqlite3.connect("/app/hickoryStrats/hickory/db/stock_db.dat")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("select * from stocks order by code asc")
    rows = c.fetchall()

    for row in rows:
        #print(row["code"])
        #st = stock_info.get_technical(row["code"])
        #stock_tech_db.manage_stock_tech(st)
        manageStock(row["code"])

def manageStockTech(code):
    
    st = stock_info.get_technical(code)
    result = stock_tech_db.manage_stock_tech(st)
    return result

def generate_TECH_MT(num_workers=1):

    conn = sqlite3.connect("/app/hickoryStrats/hickory/db/stock_db.dat")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("select * from stocks order by code asc")
    rows = c.fetchall()

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Start the load operations and mark each future with its URL
        future_to_manage = {executor.submit(manageStockTech, row["code"]): row for row in rows}
        
        for future in concurrent.futures.as_completed(future_to_manage):
            row = future_to_manage[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (row["code"], exc))
            else:
                if (data == False):
                    print('%r result is %s' % (row["code"], data))    

def manageStockVol(code):
    
    st = stock_quote.get_stock_quote(code)
    print(code + " - " + st["Close"] + "/" + st["ChangePercent"] + "/" +  st["Volume"])
    result = stock_tech_db.update_stock_vol(code, st["Close"], st["ChangePercent"], stock_util.rf(st["Volume"]))
    return result


def generate_VOL_MT(stocks, num_workers=1):

    print(stocks)

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
            else:
                if (data == False):
                    print('%r result is %s' % (code, data))    

def main(args):

    start_time = time.time()
    NO_OF_WORKER = 5

    if (len(args) > 1 and args[1] == "gen_tech"):
        generate_TECH_MT(NO_OF_WORKER)
    elif (len(args) > 1 and args[1] == "gen_vol"):
        #for period in ["1m", "3m", "1y"]:
        generate_VOL_MT(stock_sector_db.get_hot_stocks_code("ALL"), NO_OF_WORKER-1)
        sector_heatmap.generate() 

    else:
        print("OPTS: gen_tech | gen_vol")

    #generate()
    print("Time elapsed: " + "%.3f" % (time.time() - start_time) + "s")

if __name__ == "__main__":
    main(sys.argv) 
