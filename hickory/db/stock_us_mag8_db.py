#!/usr/bin/python
import sqlite3
import sys
import datetime
from datetime import tzinfo, timedelta, datetime

DB_FILE = '/app/hickoryStrats/hickory/db/stock_us_db.dat'

MAIN_WHERE_CLAUSE = "  and _150_DAY_MA >= _200_DAY_MA AND _50_DAY_MA > _150_DAY_MA and _30_DAY_MA > _200_DAY_MA and _52WEEK_HSI_RELATIVE >= 20 AND LAST_CLOSE > _150_DAY_MA AND LAST_CLOSE > _200_DAY_MA AND LAST_CLOSE > _50_DAY_MA AND LAST_CLOSE > _100_DAY_MA AND (LAST_CLOSE - _52WEEK_LOW)/_52WEEK_LOW >= 0.3 AND LAST_CLOSE > _52WEEK_HIGH * 0.75 AND _3MONTH_AVG_TURNOVER >= 1.5 * 1000000 "

def init():

    conn = sqlite3.connect(DB_FILE)
    print("Opened database successfully")
    conn.close()

def get_mag8_stocks_list():

    conn = sqlite3.connect(DB_FILE)
    stocks_us = []

    sql = ("select code from stocks_us_tech "
            + " where 1=1 " + MAIN_WHERE_CLAUSE + ";")

    c = conn.cursor()
    c.execute(sql)
    
    stocks_us = [row[0] for row in c.fetchall()]
    return stocks_us

def update_mag8_stocks_entry():

    conn = sqlite3.connect(DB_FILE)
    stocks_us = []

    # Update exit stocks_us
    sql = ("update stocks_us_tech set Y8_ENTRY_DATE = null, Y8_ENTRY_PRICE = null "
            + " WHERE Y8_ENTRY_DATE is not null "
            + " AND CODE NOT IN "
            + " (SELECT CODE FROM STOCKS_US_TECH " 
            + " WHERE 1=1 " + MAIN_WHERE_CLAUSE + " );")

    c = conn.cursor()
    c.execute(sql)
    
    # Update new stocks_us
    sql = ("update stocks_us_tech set Y8_ENTRY_DATE = ?, Y8_ENTRY_PRICE = LAST_CLOSE"
            + " WHERE Y8_ENTRY_DATE is null "
            +  MAIN_WHERE_CLAUSE + ";")

    sDate = datetime.today().strftime('%Y%m%d')
    t = (sDate,)
    c = conn.cursor()
    c.execute(sql, t)

    conn.commit()
    conn.close()

def get_mag8_stocks_dict(limit):

    conn = sqlite3.connect(DB_FILE)

    stocks_us = []
        
    sql = (" select STOCKS_US.code from stocks_us, stocks_us_tech "
            + " where stocks_us.code = stocks_us_tech.code "          
            + MAIN_WHERE_CLAUSE
            + " ORDER BY Y8_ROC_MARK DESC "
            + " LIMIT " + str(limit) + ";")       
            #+ " ORDER BY _52WEEK_HSI_RELATIVE DESC;")       
    print(sql) 
    c = conn.cursor()
    c.execute(sql)
    
    sdict = {}
    rownum = 1

    # get column names
    for row in c.fetchall():
        sdict[row[0]] = rownum
        rownum = rownum + 1
    
    print(sdict)    
    return sdict 


def get_mag8_stocks():

    conn = sqlite3.connect(DB_FILE)

    stocks_us = []
        
    sql = (" select STOCKS_US.name as stockname, STOCKS_US.INDUSTRY_LV2, STOCKS_US_TECH.* from stocks_us, stocks_us_tech "
            + " where stocks_us.code = stocks_us_tech.code "          
            + MAIN_WHERE_CLAUSE
            + " ORDER BY Y8_ROC_MARK DESC;")       
            #+ " ORDER BY _52WEEK_HSI_RELATIVE DESC;")       

    print(sql) 
    c = conn.cursor()
    c.execute(sql)
        
    # get column names
    names = [d[0] for d in c.description]
    stocks_us = [dict(zip(names, row)) for row in c.fetchall()]
    
    #print(len(stocks_us))    
    return stocks_us

def get_full_stocks_by_vol():

    conn = sqlite3.connect(DB_FILE)

    stocks_us = []
        
    sql = (" select STOCKS_US.name as stockname, STOCKS_US.INDUSTRY_LV1, STOCKS_US.INDUSTRY_LV2, STOCKS_US_TECH.* from stocks_us, stocks_us_tech "
            + " where stocks_us.code = stocks_us_tech.code "          
            + " and last_close is not null "
            + " ORDER BY LAST_VOL_RATIO DESC;")       
 
    c = conn.cursor()
    c.execute(sql)
        
    # get column names
    names = [d[0] for d in c.description]
    stocks_us = [dict(zip(names, row)) for row in c.fetchall()]
    
    #print(len(stocks_us))    
    return stocks_us

def main(args):

    if (args and args[0] == "init"):
        init()

    #update_mag8_stocks_us_entry()
    #print(get_mag8_stocks_us())
    #print(get_mag8_stocks_list())
    print(get_mag8_stocks_dict(100))
    #print(get_full_stocks_us_by_vol())

if __name__ == "__main__":
    main(sys.argv[1:])        
        

