#!/usr/bin/python
import sqlite3
import sys

DB_FILE = '/app/hickoryStrats/hickory/db/stock_us_db.dat'

def init():

    conn = sqlite3.connect(DB_FILE)

    print("Opened database successfully")
    
    conn.execute('DROP TABLE IF EXISTS STOCKS_US_TECH;')
    
    conn.execute('''CREATE TABLE STOCKS_US_TECH 
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       CODE                 TEXT    NOT NULL,
       EPS                  NUMERIC,
       PE                   NUMERIC,
       DPS                  NUMERIC,
       YIELD                NUMERIC,
       _1MONTH_CHANGE        NUMERIC,
       _3MONTH_CHANGE        NUMERIC,
       _52WEEK_CHANGE        NUMERIC,
       _1MONTH_HSI_RELATIVE  NUMERIC,
       _3MONTH_HSI_RELATIVE  NUMERIC,
       _52WEEK_HSI_RELATIVE  NUMERIC,
       MARKET_CAPITAL       NUMERIC,
       _52WEEK_HIGH          NUMERIC,
       _52WEEK_LOW           NUMERIC,
       _1MONTH_AVG_VOL       NUMERIC,
       _3MONTH_AVG_VOL       NUMERIC,
       LAST_CLOSE           NUMERIC,
       LAST_CHANGE_PCT      TEXT,
       LAST_VOL_RATIO       NUMERIC,
       _1MONTH_AVG_TURNOVER NUMERIC,
       _3MONTH_AVG_TURNOVER NUMERIC,
       _10_DAY_MA            NUMERIC,
       _30_DAY_MA           NUMERIC,
       _50_DAY_MA            NUMERIC,
       _90_DAY_MA            NUMERIC,
       _250_DAY_MA           NUMERIC,
       _14_DAY_RSI           NUMERIC,
       _100_DAY_MA          NUMERIC,
       _150_DAY_MA          NUMERIC,
       _200_DAY_MA          NUMERIC,
       Y8_ENTRY_DATE        TEXT,
       Y8_ENTRY_PRICE       NUMERIC,
       MACD_X_OVER_DATE     TEXT,
       MACD_DIVERGENCE      NUMERIC,
       _3MONTH_CLOSE       NUMERIC,
       _6MONTH_CLOSE       NUMERIC,
       _9MONTH_CLOSE       NUMERIC,
       _12MONTH_CLOSE       NUMERIC,
       Y8_ROC_MARK          NUMERIC
       );''')

    print("Table created successfully")

    conn.close()

def list_stocks_tech():
    
    conn = sqlite3.connect(DB_FILE)
    print("list the stocks...")
    for row in conn.execute("SELECT * FROM STOCKS_US_TECH ORDER BY CODE ASC"):
        print(row)

    conn.close()

def get_stock_tech(code):

    code = code.zfill(5)

    conn = sqlite3.connect(DB_FILE)

    stock = {}

    sql = "select * from stocks_us_tech where code = ?"
    t = (code,)

    c = conn.cursor()
    c.execute(sql, t)
    
    names = [d[0] for d in c.description]
   
    rows = c.fetchall() 
    if (rows):
        stock = [dict(zip(names, row)) for row in rows][0]
    conn.close()
    
    return stock

def get_all_stocks_code():

    conn = sqlite3.connect(DB_FILE)
    stocks = []

    sql = "select code from stocks_us_tech order by code"
    c = conn.cursor()
    c.execute(sql)

    rows = c.fetchall()
    for row in rows:
        stocks.append(row[0])

    conn.close()
    return stocks

def manage_stock_tech(stock_tuple):

    conn = sqlite3.connect(DB_FILE)

    t = (stock_tuple[0], )
    cursor = conn.execute('SELECT 1 FROM STOCKS_US_TECH WHERE CODE=?', t)
    
    # There is record already
    if (cursor.fetchone()):
 
        s = "UPDATE STOCKS_US_TECH SET EPS=?, PE=?, DPS=?, YIELD=?, _1MONTH_CHANGE=?, _3MONTH_CHANGE=?, _52WEEK_CHANGE=?, _1MONTH_HSI_RELATIVE=?, _3MONTH_HSI_RELATIVE=?, _52WEEK_HSI_RELATIVE=?, MARKET_CAPITAL=?, _52WEEK_HIGH=?, _52WEEK_LOW=?, _1MONTH_AVG_VOL=?, _3MONTH_AVG_VOL=?, LAST_CLOSE=?, _1MONTH_AVG_TURNOVER=?, _3MONTH_AVG_TURNOVER=?, _10_DAY_MA=?, _50_DAY_MA=?, _90_DAY_MA=?, _250_DAY_MA=?, _30_DAY_MA=?, _100_DAY_MA=?, _150_DAY_MA=?, _200_DAY_MA=?, _3MONTH_CLOSE=?, _6MONTH_CLOSE=?, _9MONTH_CLOSE=?, _12MONTH_CLOSE=?, Y8_ROC_MARK=? WHERE CODE=?"

        t = (stock_tuple[1:]) + (stock_tuple[0],)
 
        conn.execute(s, t)
        conn.commit()
        conn.close()
        print("[" + stock_tuple[0] + "] TECH INFO UPDATED - " + stock_tuple[1])
        return True
    # Blank new case
    else:

        t = stock_tuple
        print(t)
        conn.execute("INSERT INTO STOCKS_US_TECH (CODE, EPS, PE, DPS, YIELD, _1MONTH_CHANGE, _3MONTH_CHANGE, _52WEEK_CHANGE, _1MONTH_HSI_RELATIVE, _3MONTH_HSI_RELATIVE, _52WEEK_HSI_RELATIVE, MARKET_CAPITAL, _52WEEK_HIGH, _52WEEK_LOW, _1MONTH_AVG_VOL, _3MONTH_AVG_VOL, LAST_CLOSE, _1MONTH_AVG_TURNOVER, _3MONTH_AVG_TURNOVER, _10_DAY_MA, _50_DAY_MA, _90_DAY_MA, _250_DAY_MA, _30_DAY_MA, _100_DAY_MA, _150_DAY_MA, _200_DAY_MA, _3MONTH_CLOSE, _6MONTH_CLOSE, _9MONTH_CLOSE, _12MONTH_CLOSE, Y8_ROC_MARK) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", t)
        conn.commit()
        conn.close()
        print("[" + stock_tuple[0] + "] TECH INFO INSERTED - " + stock_tuple[1])
        return True

def update_stock_macd(code, macd_date, divergence):

    conn = sqlite3.connect(DB_FILE)

    t = (macd_date, divergence, code)
    conn.execute("UPDATE STOCKS_US_TECH SET MACD_X_OVER_DATE=?, MACD_DIVERGENCE=? WHERE CODE = ?", t)
    conn.commit()
    conn.close()
    return True

def update_stock_vol(code, last_close, last_change_pct, last_vol):

    conn = sqlite3.connect(DB_FILE)

    t = (last_close, last_change_pct, last_vol, code)
    conn.execute("UPDATE STOCKS_US_TECH SET LAST_CLOSE=?, LAST_CHANGE_PCT=?, LAST_VOL_RATIO=?/_3MONTH_AVG_VOL WHERE CODE = ?", t)
    conn.commit()
    conn.close()
    return True
    

def remove_stock(code):

    conn = sqlite3.connect(DB_FILE)

    t = (code,)
    conn.execute("DELETE FROM STOCKS_US_TECH WHERE CODE = ?", t)
    conn.commit()
    conn.close()
    return True
    

def main(args):

    if (args and args[0] == "init"):
        init()
    #print(manage_stock('CORP', '1357','MEITU','APP','APP','APP', 500, 230000000000000))
    #print(add_warning('04/07/2017 18:33','+'))
    #print(add_warning('04/07/2017 18:33','+'))
    #print(add_warning('04/07/2017 19:32','-'))
    #print(add_warning('04/07/2017 19:32','-'))
    #add_tracker('20170713', '823', 60.20, 'D', 'M1, D1', 'HK')
    #add_tracker('20170713', '1', 80.20, 'D', 'M1, D1')
    #list_tracker()    
    #remove_tracker('20170713', '823', 'D')
    #list_stocks()
    #remove_stock('1357')
    #list_stocks_tech()
    #print(get_stock_tech("8229"))
    print(get_stock_tech("MSFT"))
    #print(get_all_stocks_code())
 
if __name__ == "__main__":
    main(sys.argv[1:])        
        

