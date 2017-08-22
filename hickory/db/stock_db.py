#!/usr/bin/python
import sqlite3
import sys

DB_FILE = '/app/hickoryStrats/hickory/db/stock_db.dat'

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
       MKT_CAP            NUMERIC
       );''')

    print("Table created successfully")

    conn.close()

def list_stocks():
    
    conn = sqlite3.connect(DB_FILE)
    print("list the stocks...")
    for row in conn.execute("SELECT * FROM STOCKS ORDER BY CODE ASC"):
        print(row)

    conn.close()

def manage_stock(cat, code, name, industryLv1, industryLv2, industryLv3, lotSize, mktCap):

    conn = sqlite3.connect(DB_FILE)

    t = (code,)
    cursor = conn.execute('SELECT * FROM STOCKS WHERE CODE=?', t)
    
    # There is record already
    if (cursor.fetchone()):
        t = (cat, name, industryLv1, industryLv2, industryLv3, lotSize, mktCap, code)
        conn.execute("UPDATE STOCKS SET CAT=?, NAME=?, INDUSTRY_LV1=?, INDUSTRY_LV2=?, INDUSTRY_LV3=?, LOT_SIZE=?, MKT_CAP=? WHERE CODE=?", t)
        conn.commit()
        conn.close()
        return True
    # Blank new case
    else:
        t = (cat, code, name, industryLv1, industryLv2, industryLv3, lotSize, mktCap)
        conn.execute("INSERT INTO STOCKS (CAT, CODE, NAME, INDUSTRY_LV1, INDUSTRY_LV2, INDUSTRY_LV3, LOT_SIZE, MKT_CAP) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", t)
        conn.commit()
        conn.close()
        return True

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
    list_stocks()
 
if __name__ == "__main__":
    main(sys.argv[1:])        
        

