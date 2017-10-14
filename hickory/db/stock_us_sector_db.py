#!/usr/bin/python
import sqlite3
import sys

DB_FILE = '/app/hickoryStrats/hickory/db/stock_us_db.dat'
F_TURNOVER = '_3MONTH_AVG_TURNOVER'
F_RELATIVE_MAP = {'1m':'_1MONTH_HSI_RELATIVE', '3m':'_3MONTH_HSI_RELATIVE', '1y':'_52WEEK_HSI_RELATIVE'}
LIMIT_MKT_CAP = 0.5 * 100000000
LIMIT_TURNOVER = 0 * 1000000
LIMIT_HOT = "120"
THRESHOLD_RS = "30"

def init():

    conn = sqlite3.connect(DB_FILE)

    print("Opened database successfully")
    
    conn.close()
    
def get_hot_stocks_where_sql(period):

    where_sql = (" from stocks_us_tech, stocks_us where stocks_us.code = stocks_us_tech.code and "
            + F_TURNOVER + " >= ? and stocks_us_tech.MARKET_CAPITAL > ? and "
            + F_RELATIVE_MAP[period] + " > " + THRESHOLD_RS
            + " order by " + F_RELATIVE_MAP[period] + " desc limit " + LIMIT_HOT)
            
    return where_sql

def get_hot_stocks_code(period):

    conn = sqlite3.connect(DB_FILE)

    stocks_us = []

    if (period in F_RELATIVE_MAP):

        t = (LIMIT_TURNOVER, LIMIT_MKT_CAP)
        sql = ("select stocks_us.code"
            + get_hot_stocks_where_sql(period) + ";")

    elif (period == "ALL"):
        t = (LIMIT_TURNOVER, LIMIT_MKT_CAP, LIMIT_TURNOVER, LIMIT_MKT_CAP, LIMIT_TURNOVER, LIMIT_MKT_CAP)

        sql = ("select code from ("
            + "select * from (Select stocks_us.code"
            + get_hot_stocks_where_sql("1m") + ") "
            + " UNION "
            + "select * from (Select stocks_us.code"
            + get_hot_stocks_where_sql("3m") + ") "
            + "UNION "
            + "select * from (Select stocks_us.code"
            + get_hot_stocks_where_sql("1y") + ") "
            + " );")
    
    c = conn.cursor()
    c.execute(sql, t)

    stocks_us = [row[0] for row in c.fetchall()]

    #print("Size: " + str(len(stocks_us)))
    return stocks_us


def get_hot_stocks_by_industry(industry, period="ALL"):

    conn = sqlite3.connect(DB_FILE)

    stocks_us = []

    if (period in F_RELATIVE_MAP):

        t = (LIMIT_TURNOVER, LIMIT_MKT_CAP, industry)
        sql = ("select * from (select stocks_us.code, stocks_us.industry_lv2, stocks_us.name, stocks_us_tech.*"
            + get_hot_stocks_where_sql(period) + " ) where INDUSTRY_LV2 = ? order by " + F_RELATIVE_MAP[period] + ";")

    elif (period == "ALL"):
        t = (LIMIT_TURNOVER, LIMIT_MKT_CAP, LIMIT_TURNOVER, LIMIT_MKT_CAP, LIMIT_TURNOVER, LIMIT_MKT_CAP, industry)
        
        sql = ("select * from ("
            + "select * from (Select stocks_us.code, stocks_us.industry_lv2, stocks_us.name, stocks_us_tech.* "
            + get_hot_stocks_where_sql("1m") + ") "
            + " UNION "
            + "select * from (Select stocks_us.code, stocks_us.industry_lv2, stocks_us.name, stocks_us_tech.* "
            + get_hot_stocks_where_sql("3m") + ") "
            + "UNION "
            + "select * from (Select stocks_us.code, stocks_us.industry_lv2, stocks_us.name, stocks_us_tech.* "
            + get_hot_stocks_where_sql("1y") + ") "
            + " ) where industry_lv2 = ? order by " + F_RELATIVE_MAP["1y"] + " DESC, " 
            + F_RELATIVE_MAP["3m"] + " DESC, " + F_RELATIVE_MAP["1m"] +  " DESC;")

    #print(sql)
    c = conn.cursor()
    c.execute(sql, t)
        
    # get column names
    names = [d[0] for d in c.description]
    stocks_us = [dict(zip(names, row)) for row in c.fetchall()]
    
    #print(len(stocks_us))    
    return stocks_us

def get_hot_industries(period):

    conn = sqlite3.connect(DB_FILE)

    industry = []

    if (period in F_RELATIVE_MAP):

        t = (LIMIT_TURNOVER, LIMIT_MKT_CAP)
        sql = ("select industry_lv2, count(1) as count from (select stocks_us.code, stocks_us.industry_lv2, stocks_us.name, " 
            + F_RELATIVE_MAP[period] + get_hot_stocks_where_sql(period) + " ) group by industry_lv2 order by count desc;")
    
        rows = conn.execute(sql, t)
        for row in rows:
            industry.append(row[0])
    
    elif (period == "ALL"):
        #print("Get All...")
        t = (LIMIT_TURNOVER, LIMIT_MKT_CAP, LIMIT_TURNOVER, LIMIT_MKT_CAP, LIMIT_TURNOVER, LIMIT_MKT_CAP)
        
        sql = ("select industry_lv2, count(1) as count from ("
            + "select * from (Select stocks_us.code, stocks_us.industry_lv2, stocks_us.name, "
            + F_RELATIVE_MAP['1m'] + "," + F_RELATIVE_MAP['3m'] + "," + F_RELATIVE_MAP['1y']
            + get_hot_stocks_where_sql("1m") + ") "
            + " UNION "
            + "select * from (Select stocks_us.code, stocks_us.industry_lv2, stocks_us.name, "
            + F_RELATIVE_MAP["1m"] + "," + F_RELATIVE_MAP["3m"] + "," + F_RELATIVE_MAP["1y"]
            + get_hot_stocks_where_sql("3m") + ") "           
            + "UNION "
            + "select * from (Select stocks_us.code, stocks_us.industry_lv2, stocks_us.name, "
            + F_RELATIVE_MAP["1m"] + "," + F_RELATIVE_MAP["3m"] + "," + F_RELATIVE_MAP["1y"]
            + get_hot_stocks_where_sql("1y") + ") "  
            + " ) group by industry_lv2 order by count desc;")
        #print(sql)
        rows = conn.execute(sql, t)
        for row in rows:
            industry.append(row[0])
    
    conn.close()
    
    return industry

def main(args):

    if (args and args[0] == "init"):
        init()

    #print(get_hot_industries("1m"))
    #print(get_hot_stocks_us_by_industry("公用事業","1m"))
    #print(get_hot_industries("1m"))
    #print(get_hot_industries("3m"))
    #print(get_hot_industries("1y"))
    print(get_hot_industries("ALL"))

    print(get_hot_stocks_by_industry("Oil & Gas Production"))

    #print(get_hot_stocks_us_by_industry("公用事業","1m"))
    #print(get_hot_stocks_us_by_industry("公用事業","ALL"))

    #print(get_hot_stocks_code("ALL"))

    '''import math
    industries = get_hot_industries("1m")

    num_rows = math.ceil(len(industries) / 4)

    for i in range(0, num_rows):
        for j in range(0, 4):
            if (i*4 + j < len(industries)):
                print("row" + str(i) + " - " + industries[i*4 + j])
    '''

if __name__ == "__main__":
    main(sys.argv[1:])        
        

