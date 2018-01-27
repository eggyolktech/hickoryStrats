#!/usr/bin/python

from datetime import datetime, timedelta

def get_wd_date_list(delta, numdays=10):
    
    sdate = datetime.now().date() - timedelta(days=delta)

    if (sdate.weekday() == 6):
        sdate = sdate - timedelta(days=2)
    elif (sdate.weekday() == 5):
        sdate = sdate - timedelta(days=1)

    dlst = [sdate] 

    for i in range(1, numdays):
        
        if (sdate.weekday() == 0):
            sdate = sdate - timedelta(days=3)
        else:
            sdate = sdate - timedelta(days=1)
        dlst.append(sdate)

    return dlst

def main():
    get_wd_date_list(2, 10)    

if __name__ == "__main__":
    main() 
