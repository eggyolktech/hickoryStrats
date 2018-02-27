#!/usr/bin/python
import numpy as np
import pandas as pd
import datetime
import configparser
import sys
import os
import urllib.request
import urllib.parse
import sqlite3
import locale
import concurrent.futures
import time
import traceback
import logging
import json

from datetime import tzinfo, timedelta, datetime
from hickory.util import config_loader, stock_util, mem_util, git_util
from hickory.indicator import gwc
from hickory.data import webdata
from hickory.crawler.aastocks import stock_quote, stock_info
from hickory.crawler.money18 import stock_quote as m18_stock_quote
from hickory.db import stock_tech_db, stock_sector_db, stock_db
from market_watch.telegram import bot_sender

#from hickory.report import sector_heatmap

config = config_loader.load()
EXPORT_REPO = "/app/hickoryStratsWatcher/"
EL = "\n"
DEL = "\n\n"
LIMIT=3000

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def IsMMBreakoutWithPullback(code, sbars, num_days=30, pb_days=2):

    if (len(sbars) < num_days):
        return False
    else:
        obars = sbars.tail(num_days)
        bars = obars[:-pb_days]
    
    RF = 0.2
    first_close = float(bars.head(1).iloc[0]['Close'])
    last_close = float(bars.tail(1).iloc[0]['Close'])
    last_vol = float(bars.tail(1).iloc[0]['Volume'])
    mean_vol = float(bars[:-1]['Volume'].mean())

    if (mean_vol > 0):
        vav = last_vol/mean_vol
    else:
        vav = 0

    max_high = float(bars[:-1]['High'].max())
    #print(code + " - " + str(max_high) + " ######## " + str(first_close) + " >>>>> " + str(bars[:-1]['Low'].min()))
    max_high_ratio = max_high/first_close
    min_low_ratio = float(bars[:-1]['Low'].min())/first_close

    

    conds = []
    conds.append(max_high_ratio < (1 + RF) and min_low_ratio > (1 - RF))
    conds.append(vav > 1.5)
    conds.append(last_close > max_high)

    for i in range(1, pb_days):
        conds.append(obars['Close'].iloc[-i] < obars['Open'].iloc[-i])
        conds.append(obars['Low'].iloc[-i] > bars['Low'].iloc[-i])
        conds.append(obars['Volume'].iloc[-i] < 0.5 * last_vol)
    
    #conds.append(obars['Close'].iloc[-1] < obars['Open'].iloc[-1])
    #conds.append(obars['Close'].iloc[-2] < obars['Open'].iloc[-2])
    #conds.append(obars['Low'].iloc[-1] > bars['Low'].iloc[-1])
    #conds.append(obars['Low'].iloc[-2] > bars['Low'].iloc[-2])
    #conds.append(obars['Volume'].iloc[-1] < 0.5 * last_vol)
    #conds.append(obars['Volume'].iloc[-2] < 0.5 * last_vol)
    
    result = not (False in conds)
    
    #if (result):
    #    print(conds)
    #return conds
    return result

def IsMMInverseBreakout(code, sbars, num_days=30):

    if (len(sbars) < num_days):
        return False
    else:
        bars = sbars.tail(num_days)
    
    RF = 0.2
    first_close = float(bars.head(1).iloc[0]['Close'])
    last_close = float(bars.tail(1).iloc[0]['Close'])
    
    last_open = float(bars.tail(1).iloc[0]['Open'])
    last_low = float(bars.tail(1).iloc[0]['Low'])
    last_high = float(bars.tail(1).iloc[0]['High'])
    
    last_vol = float(bars.tail(1).iloc[0]['Volume'])
    mean_vol = float(bars[:-1]['Volume'].mean())

    if (mean_vol > 0):
        vav = last_vol/mean_vol
    else:
        vav = 0
 
    max_high = float(bars[:-1]['High'].max())
    min_low = float(bars[:-1]['Low'].min())
    #print(code + " - " + str(max_high) + " ######## " + str(first_close) + " >>>>> " + str(bars[:-1]['Low'].min()))
    max_high_ratio = max_high/first_close
    min_low_ratio = min_low/first_close

    conds = []
    conds.append(max_high_ratio < (1 + RF) and min_low_ratio > (1 - RF))
    #conds.append(vav > 1.5)
    conds.append(last_low < min_low)
    conds.append(last_close > min_low)
    conds.append(last_close > last_open)
    result = not (False in conds)
    
    #if (result):
    #    print(conds)
    #return conds
    return result

def IsMMBreakout(code, sbars, num_days=30):

    #print(len(bars))
    if (len(sbars) < num_days):
        return False
    else:
        bars = sbars.tail(num_days)
    
    RF = 0.2
    first_close = float(bars.head(1).iloc[0]['Close'])
    last_close = float(bars.tail(1).iloc[0]['Close'])
    last_vol = float(bars.tail(1).iloc[0]['Volume'])
    mean_vol = float(bars[:-1]['Volume'].mean())

    if (mean_vol > 0):
        vav = last_vol/mean_vol
    else:
        vav = 0

    max_high = float(bars[:-1]['High'].max())
    #print(code + " - " + str(max_high) + " ######## " + str(first_close) + " >>>>> " + str(bars[:-1]['Low'].min()))
    max_high_ratio = max_high/first_close
    min_low_ratio = float(bars[:-1]['Low'].min())/first_close

    conds = []
    conds.append(max_high_ratio < (1 + RF) and min_low_ratio > (1 - RF))
    conds.append(vav > 1.5)
    conds.append(last_close > max_high)
    result = not (False in conds)
    
    #if (result):
    #    print(conds)
    #return conds
    return result

def manageInverseStockSignals(code, num_months=1):

    ycode = code.lstrip("0");

    if (is_number(ycode)):
        ycode = ycode.rjust(4, '0') + ".HK"
   
    end = datetime.today()
    start = end - timedelta(days=(num_months*30))

    bars = webdata.DataReader(ycode, "yahoo_direct", start, end)
    bars['Volume'] = bars['Volume'].replace('null', 0)
    
    if (len(bars) == 0):
        #print(code + " - no data found")
        return True

    #print(bars)
    #print(bars['Close'])

    #if (IsMMBreakout(bars)):
    #    print(code + " - IsMMBreakout")

    result = []
    result.append(code)
    result.append(IsMMInverseBreakout(code, bars))
    return result

def manageWeeklyStockSignals(code, num_months=1):

    ycode = code.lstrip("0");

    if (is_number(ycode)):
        ycode = ycode.rjust(4, '0') + ".HK"
   
    end = datetime.today()
    start = end - timedelta(days=(num_months*30))

    bars = webdata.DataReader(ycode, "yahoo_direct", start, end)
    bars['Volume'] = bars['Volume'].replace('null', 0)
    
    if (len(bars) == 0):
        #print(code + " - no data found")
        return True

    #print(bars)
    #print(bars['Close'])

    #if (IsMMBreakout(bars)):
    #    print(code + " - IsMMBreakout")

    result = []
    result.append(code)
    result.append(IsMMBreakout(code, bars))
    result.append(IsMMBreakoutWithPullback(code, bars, 30, 2))
    result.append(IsMMBreakoutWithPullback(code, bars, 30, 3))
    
    #if (IsLowVolPullback(bars)):
    #    print(code + " - IsLowVolPullback")
    
    #result = True
    return result



def manageStockSignals(code, num_months=1):

    ycode = code.lstrip("0");

    if (is_number(ycode)):
        ycode = ycode.rjust(4, '0') + ".HK"
   
    end = datetime.today()
    start = end - timedelta(days=(num_months*30))

    bars = webdata.DataReader(ycode, "yahoo_direct", start, end)
    bars['Volume'] = bars['Volume'].replace('null', 0)
    
    if (len(bars) == 0):
        #print(code + " - no data found")
        return True

    #print(bars)
    #print(bars['Close'])

    #if (IsMMBreakout(bars)):
    #    print(code + " - IsMMBreakout")

    result = []
    result.append(code)
    result.append(IsMMBreakout(code, bars))
    result.append(IsMMBreakoutWithPullback(code, bars, 30, 2))
    result.append(IsMMBreakoutWithPullback(code, bars, 30, 3))
    
    #if (IsLowVolPullback(bars)):
    #    print(code + " - IsLowVolPullback")
    
    #result = True
    return result

def generate_SIG_MT(num_workers, signalType):

    conn = sqlite3.connect("/app/hickoryStrats/hickory/db/stock_db.dat")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("select * from stocks order by code asc")
    rows = c.fetchall()
    isInv = False

    if (signalType == "NORMAL"):
        sigFun = manageStockSignals
    elif (signalType == "INVERSE"):
        sigFun = manageInverseStockSignals
        isInv = True
    else:
        sigFun = manageStockSignals

    data_list = []

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Start the load operations and mark each future with its URL
        future_to_manage = {executor.submit(sigFun, row["code"], 4): row for row in rows[:LIMIT]}
        
        for future in concurrent.futures.as_completed(future_to_manage):
            row = future_to_manage[future]
            try:
                data = future.result(timeout=15)
                data_list.append(data)
            except concurrent.futures.TimeoutError:
                logging.error("%r took too long to run..." % (row["code"]))
            except Exception as exc:
                #print('%r generated an exception: %s' % (row["code"], exc))
                logging.error(" Error retrieving code: " + row["code"])
                #logging.error(traceback.format_exc())
            else:
                if (data == False):
                    print('%r result is %s' % (row["code"], data))    

        try:
            if (isInv):
                mm = u'\U0001F422' +  u'\U0001F422' + u'\U00002198' + u'\U00002197' + " List"
            else:
                mm = u'\U0001F422' +  u'\U0001F422' + u'\U0001F199' + " List"

            t1 = mm + '\n\n'
            t2 = mm + " with "  + u'\U00000032' + " " +  u'\U0000303D' + '\n\n'
            t3 = mm + " with "  + u'\U00000033' + " " +  u'\U0000303D' + '\n\n'
            p1 = p2 = p3 = ""
            list_data = []
            datalist = {} 
            list_datalist = []
            masterdata = {}

            for d in data_list:
                rcode = d[0]

                # for generate watcher js
                stock = {}
                stock["code"] = rcode
                stock["label"] = stock_db.get_stock_name(rcode)
                list_data.append(stock)            

                # for generate telegram messages
                if (d[1] == True):
                    alt = ""
                    if (stock_quote.is_52weekhigh(rcode)):
                        alt = u'\U0001F525'     
                    p1 = p1 + "/qd" + rcode + " - " + alt + stock_db.get_stock_name(rcode) + " (" + stock_db.get_stock_industry(rcode) + ")" + '\n'
                if (len(d) > 3 and d[2] == True):
                    p2 = p2 + "/qd" + rcode + " - " + stock_db.get_stock_name(rcode) + " (" + stock_db.get_stock_industry(rcode) + ")" + '\n'
                if (len(d) > 3 and d[3] == True):
                    p3 = p3 + "/qd" + rcode + " - " + stock_db.get_stock_name(rcode) + " (" + stock_db.get_stock_industry(rcode) + ")" + '\n'

            # generate watcher js
            if (list_data):
                datalist["code"] = "DAILY_BreakOutList_" + datetime.today().strftime('%y%m%d')
                datalist["list"] = list_data
                datalist["label"] = datalist["code"] + "_" + str(len(list_data))
                list_datalist.append(datalist)
                masterdata["list"] = list_datalist
                json_data = json.dumps(masterdata)
                print(json_data)

                filesub = "web/js/"
                filedir = EXPORT_REPO + filesub
                filepath = "dailyWatcherBreakoutListData.js"

                with open(filedir + filepath, 'w') as the_file:
                    the_file.write("//" + str(datetime.today()) + EL)
                    the_file.write("var " + filepath.replace(".js","") + " =" + json_data + ";")

                print("File extracted as " + filedir + filepath)

                git_util.commitAll(EXPORT_REPO)
                git_util.push_remote(EXPORT_REPO)

            # send telegram messages
            isTest = False
            if (p1):
                bot_sender.broadcast(str(t1 + p1), isTest)
            if (p2):
                bot_sender.broadcast(str(t2 + p2), isTest)
            if (p3):
                bot_sender.broadcast(str(t3 + p3), isTest)
        
        except Exception:
                logging.error(traceback.format_exc())

def generate_WEEKLY_SIG_MT(num_workers, signalType):

    conn = sqlite3.connect("/app/hickoryStrats/hickory/db/stock_db.dat")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("select * from stocks order by code asc")
    rows = c.fetchall()
    isInv = False

    if (signalType == "NORMAL"):
        sigFun = manageWeeklyStockSignals
    else:
        sigFun = manageWeeklyStockSignals

    data_list = []

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Start the load operations and mark each future with its URL
        future_to_manage = {executor.submit(sigFun, row["code"], 4): row for row in rows[:LIMIT]}
        
        for future in concurrent.futures.as_completed(future_to_manage):
            row = future_to_manage[future]
            try:
                data = future.result(timeout=15)
                data_list.append(data)
            except concurrent.futures.TimeoutError:
                logging.error("%r took too long to run..." % (row["code"]))
            except Exception as exc:
                #print('%r generated an exception: %s' % (row["code"], exc))
                logging.error(" Error retrieving code: " + row["code"])
                #logging.error(traceback.format_exc())
            else:
                if (data == False):
                    print('%r result is %s' % (row["code"], data))    

        try:
            mm = "Weekly All Time High List"
            passage = ""

            for d in data_list:
                rcode = d[0]
                print(rcode)

            # send telegram messages
            isTest = True
            if (passage):
                bot_sender.broadcast("Weekly Test", isTest)
        
        except Exception:
                logging.error(traceback.format_exc())
            
def main(args):

    mem_util.set_max_mem(50)
    start_time = time.time()
    NO_OF_WORKER = 4 

    webdata.init_cookies_and_crumb()
    
    if (len(args) > 1 and args[1] == "gen_sig"):
        generate_SIG_MT(NO_OF_WORKER, "NORMAL")
    elif (len(args) > 1 and args[1] == "gen_invsig"):
        generate_SIG_MT(NO_OF_WORKER, "INVERSE")
    else:
        print("OPTS: gen_sig | gen_invsig")
        #print(manageStockTech("175"))

    print("Time elapsed: " + "%.3f" % (time.time() - start_time) + "s")

if __name__ == "__main__":
    main(sys.argv) 
