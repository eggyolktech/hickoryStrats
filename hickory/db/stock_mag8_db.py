#!/usr/bin/python
import sqlite3
import sys
import datetime
from datetime import tzinfo, timedelta, datetime

DB_FILE = '/app/hickoryStrats/hickory/db/stock_db.dat'

MAIN_WHERE_CLAUSE = "  and _150_DAY_MA >= _200_DAY_MA AND _50_DAY_MA > _150_DAY_MA and _30_DAY_MA > _200_DAY_MA and _52WEEK_HSI_RELATIVE >= 20 AND LAST_CLOSE > _150_DAY_MA AND LAST_CLOSE > _200_DAY_MA AND LAST_CLOSE > _50_DAY_MA AND LAST_CLOSE > _100_DAY_MA AND (LAST_CLOSE - _52WEEK_LOW)/_52WEEK_LOW >= 0.3 AND LAST_CLOSE > _52WEEK_HIGH * 0.75 AND _3MONTH_AVG_TURNOVER >= 3 * 1000000 "

def init():

    conn = sqlite3.connect(DB_FILE)
    print("Opened database successfully")
    conn.close()

def get_mag8_stocks_list():

    conn = sqlite3.connect(DB_FILE)
    stocks = []

    sql = ("select code from stocks_tech "
            + " where 1=1 " + MAIN_WHERE_CLAUSE + ";")

    c = conn.cursor()
    c.execute(sql)
    
    stocks = [row[0] for row in c.fetchall()]
    return stocks

def update_mag8_stocks_entry():

    conn = sqlite3.connect(DB_FILE)
    stocks = []

    # Update exit stocks
    sql = ("update stocks_tech set Y8_ENTRY_DATE = null, Y8_ENTRY_PRICE = null "
            + " WHERE Y8_ENTRY_DATE is not null "
            + " AND CODE NOT IN "
            + " (SELECT CODE FROM STOCKS_TECH " 
            + " WHERE 1=1 " + MAIN_WHERE_CLAUSE + " );")

    c = conn.cursor()
    c.execute(sql)
    
    # Update new stocks
    sql = ("update stocks_tech set Y8_ENTRY_DATE = ?, Y8_ENTRY_PRICE = LAST_CLOSE"
            + " WHERE Y8_ENTRY_DATE is null "
            +  MAIN_WHERE_CLAUSE + ";")

    sDate = datetime.today().strftime('%Y%m%d')
    t = (sDate,)
    c = conn.cursor()
    c.execute(sql, t)

    conn.commit()
    conn.close()

def get_mag8_stocks():

    conn = sqlite3.connect(DB_FILE)

    stocks = []
        
    sql = (" select STOCKS.name as stockname, STOCKS.INDUSTRY_LV3, STOCKS_TECH.* from stocks, stocks_tech "
            + " where stocks.code = stocks_tech.code "          
            + MAIN_WHERE_CLAUSE
            + " ORDER BY _52WEEK_HSI_RELATIVE DESC;")       
 
    c = conn.cursor()
    c.execute(sql)
        
    # get column names
    names = [d[0] for d in c.description]
    stocks = [dict(zip(names, row)) for row in c.fetchall()]
    
    #print(len(stocks))    
    return stocks

def get_full_stocks_by_vol():

    conn = sqlite3.connect(DB_FILE)

    stocks = []
        
    sql = (" select STOCKS.name as stockname, STOCKS.INDUSTRY_LV2, STOCKS_TECH.* from stocks, stocks_tech "
            + " where stocks.code = stocks_tech.code "          
            + " and last_close is not null "
            + " ORDER BY LAST_VOL_RATIO DESC;")       
 
    c = conn.cursor()
    c.execute(sql)
        
    # get column names
    names = [d[0] for d in c.description]
    stocks = [dict(zip(names, row)) for row in c.fetchall()]
    
    #print(len(stocks))    
    return stocks

def main(args):

    if (args and args[0] == "init"):
        init()

    update_mag8_stocks_entry()
    print(get_mag8_stocks())
    print(get_mag8_stocks_list())

if __name__ == "__main__":
    main(sys.argv[1:])        
        

