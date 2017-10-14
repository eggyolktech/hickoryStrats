#!/usr/bin/python

from hickory.db import stock_us_db

RUSSELL_FILE = "Russell_3000_Intraday.txt"

def parse_file():

    with open(RUSSELL_FILE) as f:
        lines = f.readlines()
        startParse = False
        num = 1

        for line in lines:
            if (startParse):
                tab_arr = [x for x in line.split('\t')]
                if (len(tab_arr) > 1):
                    code = tab_arr[1]
                    name = tab_arr[4].strip('"')
                    if (tab_arr[6].strip('"')):
                        industry = tab_arr[6].replace("\n", "").strip('"')
                    else:
                        industry = "Others"
                    if (tab_arr[7].rstrip().strip('"')):
                        sector = tab_arr[7].rstrip().strip('"')
                    else:
                        sector = "Others"

                    if (stock_us_db.manage_stock(code, name, sector, industry, tab_arr[2], tab_arr[5])):
                        print(str(num) + ". " + code + " -- " + name + " [" + sector + " > " + industry + "] is added")
                    else:
                        print(str(num) + ". " + code + " -- " + name + " [" + sector + " > " + industry + "] add failed")
    
                    num = num + 1
                else:
                    break
                
            if ("Symbol" in line):
                startParse = True

def main():

    parse_file()

 
if __name__ == "__main__":
    main()                
              



