#!/usr/bin/python
import sqlite3
import sys
import datetime
from datetime import tzinfo, timedelta, datetime
from hickory.crawler.hkex import mutual_market

DB_FILE = '/app/hickoryStrats/hickory/db/stock_db.dat'

def init():

    conn = sqlite3.connect(DB_FILE)
    print("Opened database successfully")
    conn.close()

def get_mf_stocks():

    conn = sqlite3.connect(DB_FILE)

    stocks = []

    stocklist = mutual_market.get_moneyflow_stocks()

    placeholders = ','.join('?' for i in range(len(stocklist)))
        
    sql = (" select STOCKS.name as stockname, STOCKS.INDUSTRY_LV3, STOCKS_TECH.* from stocks, stocks_tech "
            + " where stocks.code = stocks_tech.code "          
            + " and stocks.code in (%s)" % placeholders
            + " ORDER BY _52WEEK_HSI_RELATIVE DESC;")       
 
    c = conn.cursor()
    c.execute(sql, stocklist)
        
    # get column names
    names = [d[0] for d in c.description]
    stocks = [dict(zip(names, row)) for row in c.fetchall()]
    
    #print(len(stocks))    
    return stocks

def main(args):

    if (args and args[0] == "init"):
        init()

    print(get_mf_stocks())

if __name__ == "__main__":
    main(sys.argv[1:])        
        

