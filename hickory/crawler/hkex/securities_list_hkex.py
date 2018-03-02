#!/usr/bin/python

# Import pandas
import pandas as pd
from hickory.crawler.hkex import sync_stocks_list

def main():
    
    # Assign spreadsheet filename to `file`
    file = 'C:\Temp\ListOfSecurities.xlsx'

    # Load spreadsheet
    xl = pd.ExcelFile(file)

    # Print the sheet names
    print(xl.sheet_names)

    # Load a sheet into a DataFrame by name: df1
    df1 = xl.parse('ListOfSecurities')
    dff = df1[2:]
    
    FILTER_CAT = ["Debt Securities", "Equity Warrants", "Derivative Warrants", "Callable Bull"]
    
    for index, row in dff.iterrows():
        is_sec = True
        for cat in FILTER_CAT:
            if cat in row[2]:
                is_sec = False
                
        if (is_sec and int(row[0]) > 256):
            print(row[0] + " - " + row[1] + " (" + row[2] + ")")            
            sync_stocks_list.get_hkex_equ_dtl(row[0].strip())
    
    #print(dflist[dflist.columns[0]])

 
if __name__ == "__main__":
    main()                
              



