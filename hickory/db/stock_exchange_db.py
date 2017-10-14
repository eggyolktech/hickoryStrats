#!/usr/bin/python
import sqlite3
import sys

DB_FILE = '/app/hickoryStrats/hickory/db/stock_exchange_db.dat'

def init():

    conn = sqlite3.connect(DB_FILE)

    print("Opened database successfully")
    
    conn.execute('DROP TABLE IF EXISTS STOCKS_EX;')
    
    conn.execute('''CREATE TABLE STOCKS_EX 
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       CODE               TEXT    NOT NULL,
       NAME               TEXT    NOT NULL,
       EXCHANGE           TEXT    NOT NULL
       );''')

    print("Table created successfully")

    conn.close()

def list_stocks():
    
    conn = sqlite3.connect(DB_FILE)
    print("list the stocks...")
    for row in conn.execute("SELECT * FROM STOCKS_EX ORDER BY CODE ASC"):
        print(row)

    conn.close()

def manage_stock(code, name, industryLv1, industryLv2, since, exchange):

    conn = sqlite3.connect(DB_FILE)

    t = (code,)
    cursor = conn.execute('SELECT * FROM STOCKS_EX WHERE CODE=?', t)
    
    # There is record already
    if (cursor.fetchone()):
        t = (name, industryLv1, industryLv2, since, exchange, code)
        conn.execute("UPDATE STOCKS_EX SET NAME=?, EXCHANGE=? WHERE CODE=?", t)
        conn.commit()
        conn.close()
        return True
    # Blank new case
    else:
        t = (code, name, industryLv1, industryLv2, since, exchange)
        conn.execute("INSERT INTO STOCKS_EX (CODE, NAME, EXCHANGE) VALUES (?, ?, ?)", t)
        conn.commit()
        conn.close()
        return True

def get_stock_ex(code):

    conn = sqlite3.connect(DB_FILE)
    name = None
    exchange = None
    code = code.replace(".US","")

    t = (code,)
    for row in conn.execute("SELECT NAME, EXCHANGE FROM STOCKS_EX WHERE CODE=?", t):
        name = row[0]
        exchange = row[1]
    
    conn.close()
    return [name, exchange] 

def remove_stock(code):

    conn = sqlite3.connect(DB_FILE)

    t = (code,)
    conn.execute("DELETE FROM STOCKS_EX WHERE CODE = ?", t)
    conn.commit()
    conn.close()
    return True
    

def main(args):

    if (args and args[0] == "init"):
        init()

    list_stocks()    
    #print(get_stock_name('0087001'))
    #print(get_stock_name('3054'))
 
if __name__ == "__main__":
    main(sys.argv[1:])        
        

