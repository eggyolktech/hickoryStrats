#!/usr/bin/python

# Import pandas
import os
import time
import pandas as pd
from hickory.crawler.hkex import stock_detail 
from hickory.db import stock_db

def main():
    
    if (os.name == 'nt'):
        # Assign spreadsheet filename to `file`
        file = 'C:\Temp\ListOfSecurities.xlsx'
    else:
        file = '/tmp/ListOfSecurities.xlsx'

    # Load spreadsheet
    xl = pd.ExcelFile(file)

    # Print the sheet names
    print(xl.sheet_names)

    # Load a sheet into a DataFrame by name: df1
    df1 = xl.parse('ListOfSecurities')
    dff = df1[2:]
    
    FILTER_CAT = ["Debt Securities", "Equity Warrants", "Derivative Warrants", "Callable Bull"]
    OFFSET = 0   
 
    for index, row in dff.iterrows():
        is_sec = True
        for cat in FILTER_CAT:
            if cat in row[2]:
                is_sec = False
                
        if (is_sec and int(row[0]) >= OFFSET):
            print(row[0] + " - " + row[1] + " (" + row[2] + ")")            
            _code = str(row[0].strip())
            _stk_cat = row[2]
            try:
                get_stk_dtl(_code, _stk_cat)
            except:
                print("Failure captured...try once more after 30s")
                time.sleep(30)
                
                try:
                    get_stk_dtl(_code, _stk_cat)
                except:
                    print("Failure captured again...try last attemp after 180s")
                    time.sleep(180)
                    get_stk_dtl(_code, _stk_cat)

def get_stk_dtl(_code, _stk_cat):
 
    if (stock_db.is_stock_exist(_code)):
        print(_code + " already exists!!")
        return

    if ("Equity" in _stk_cat):
        stock_detail.get_hkex_equ_dtl(_code)
    elif ("Exchange Traded" in _stk_cat):
        stock_detail.get_hkex_etf_dtl(_code)
    elif ("Real Estate" in _stk_cat):
        stock_detail.get_hkex_reits_dtl(_code)
 
 
if __name__ == "__main__":
    main()                
              



