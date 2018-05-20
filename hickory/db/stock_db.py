#!/usr/bin/python
import sqlite3
import sys

DB_FILE = '/app/hickoryStrats/hickory/db/stock_db.dat'
#DB_FILE = '/app/hickoryStrats/hickory/db/stock_hk_db.dat'

def init():

    conn = sqlite3.connect(DB_FILE)

    print("Opened database successfully")
    
    conn.execute('DROP TABLE IF EXISTS STOCKS;')
    
    conn.execute('''CREATE TABLE STOCKS 
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       CAT                VARCHAR2(4) NOT NULL,
       CODE               TEXT    NOT NULL,
       NAME               TEXT    NOT NULL,
       INDUSTRY_LV1       TEXT    NOT NULL,
       INDUSTRY_LV2       TEXT    NOT NULL,
       INDUSTRY_LV3       TEXT    NOT NULL,
       LOT_SIZE           NUMERIC,
       MKT_CAP            NUMERIC,
       SHS_TYPE           VARCHAR2(1) 
       );''')

    print("Table created successfully")

    conn.close()

def get_stocks_list():

    conn = sqlite3.connect(DB_FILE)
    stocks_list = []

    for col in conn.execute("SELECT CODE, NAME FROM STOCKS ORDER BY CODE ASC"):
        
        stock_dict = {}
        stock_dict["code"] = col[0].lstrip("0")
        stock_dict["label"] = col[1].strip()
        stocks_list.append(stock_dict)

    conn.close()
    return stocks_list

def list_stocks():
    
    conn = sqlite3.connect(DB_FILE)
    print("list the stocks...")
    for row in conn.execute("SELECT * FROM STOCKS ORDER BY CODE ASC"):
        print(row)

    conn.close()

def is_stock_exist(code):

    conn = sqlite3.connect(DB_FILE)
    t = (code.zfill(5),)
    cursor = conn.execute('SELECT * FROM STOCKS WHERE CODE=?', t)

    # There is record already
    if (cursor.fetchone()):
        conn.close()
        return True
    
    return False

def manage_stock(cat, code, name, industryLv1, industryLv2, industryLv3, lotSize, mktCap, shsType="N"):

    conn = sqlite3.connect(DB_FILE)
    t = (code,)
    cursor = conn.execute('SELECT * FROM STOCKS WHERE CODE=?', t)
    
    # There is record already
    if (cursor.fetchone()):
        t = (cat, name, industryLv1, industryLv2, industryLv3, lotSize, mktCap, shsType, code)
        conn.execute("UPDATE STOCKS SET CAT=?, NAME=?, INDUSTRY_LV1=?, INDUSTRY_LV2=?, INDUSTRY_LV3=?, LOT_SIZE=?, MKT_CAP=?, SHS_TYPE=? WHERE CODE=?", t)
        conn.commit()
        print(code + " is updated")
        conn.close()
        return True
    # Blank new case
    else:
        t = (cat, code, name, industryLv1, industryLv2, industryLv3, lotSize, mktCap, shsType)
        conn.execute("INSERT INTO STOCKS (CAT, CODE, NAME, INDUSTRY_LV1, INDUSTRY_LV2, INDUSTRY_LV3, LOT_SIZE, MKT_CAP, SHS_TYPE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", t)
        conn.commit()
        print(code + " is added")
        conn.close()
        return True

def get_stock_shstype(code):

    conn = sqlite3.connect(DB_FILE)
    ind = None
    code = code.zfill(5)

    t = (code,)
    for row in conn.execute("SELECT SHS_TYPE FROM STOCKS WHERE CODE=?", t):
        ind = row[0]
    
    conn.close()
    return ind 

def get_stock_industry(code):

    conn = sqlite3.connect(DB_FILE)
    ind = None
    code = code.zfill(5)

    t = (code,)
    for row in conn.execute("SELECT INDUSTRY_LV3 FROM STOCKS WHERE CODE=?", t):
        ind = row[0]
    
    conn.close()
    return ind 

def get_stock_name(code):

    conn = sqlite3.connect(DB_FILE)
    name = None
    code = code.zfill(5)

    t = (code,)
    for row in conn.execute("SELECT NAME FROM STOCKS WHERE CODE=?", t):
        name = row[0]
    
    conn.close()
    return name 

def remove_stock(code):

    conn = sqlite3.connect(DB_FILE)

    t = (code,)
    conn.execute("DELETE FROM STOCKS WHERE CODE = ?", t)
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
    #list_stocks()
    #print(get_stock_name('257'))
    #print(get_stock_name('2800'))
    #print(get_stock_name('823'))

    for code in ['1','2','2800','87001','87002']:
        print(is_stock_exist(code))

    print(get_stocks_list())
 
if __name__ == "__main__":
    main(sys.argv[1:])        
        

