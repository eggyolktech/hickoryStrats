#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import locale
import json
import re
from hickory.util import stock_util
from hickory.db import stock_us_db
from datetime import datetime

EL = "\n"
DEL = "\n\n"
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

# Create a function called "chunks" with two arguments, l and n:
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]    
    
def parse_list():

    url = "https://api.iextrading.com/1.0/ref-data/symbols"

    print("URL: [" + url + "]")
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    jsondata = r.text 
    data = json.loads(jsondata)
    
    enabledList = [d for d in data if d['isEnabled'] == True and "#" not in d['symbol']]
    enabledList = enabledList
    print("Enabled List Length: %s" % len(enabledList))
 
    symbolLists = chunks([d['symbol'] for d in enabledList], 100)
    symbolDict = {}
    
    for symbolList in symbolLists:
    
        symbolStr = ','.join(symbolList)
        surl = "https://api.iextrading.com/1.0/stock/market/batch?symbols=%s&types=company" % symbolStr
        
        #if ("SSW" in symbolStr):
        #    print("##########################[%s]" % surl)
    
        r2 = requests.get(surl, headers=headers)
        jsondata2 = r2.text 
        data2 = json.loads(jsondata2)
        
        #if ("SSW" in symbolStr):
        #    print(data2)
        
        symbolDict = {**symbolDict, **data2}
        print("Processing %s/%s records...." % (len(symbolDict), len(enabledList)))
    
    print("Symbol Dict Length: %s" % len(symbolDict))
    emptySymbolList = [d for d in symbolDict.keys() if not symbolDict[d]]
    print("Empty Symbol Dict Length: %s" % len(emptySymbolList))
    
    print("Reprocessing emptySymbolList: %s" % emptySymbolList)
    symbolLists = chunks(emptySymbolList, 10)    
    for symbolList in symbolLists:
    
        symbolStr = ','.join(symbolList)
        surl = "https://api.iextrading.com/1.0/stock/market/batch?symbols=%s&types=company" % symbolStr
        
        r2 = requests.get(surl, headers=headers)
        jsondata2 = r2.text 
        data2 = json.loads(jsondata2)
        
        symbolDict = {**symbolDict, **data2}
        print("Reprocessing %s/%s records...." % (len(symbolDict), len(enabledList)))
    
    print("2nd Symbol Dict Length: %s" % len(symbolDict))
    emptySymbolList = [d for d in symbolDict.keys() if not symbolDict[d]]
    print("2nd Empty Symbol Dict Length: %s" % len(emptySymbolList))
    print(emptySymbolList)
    
    #with open('C:\Temp\dumps.txt', 'w') as file:
    #     file.write(json.dumps(symbolDict)) # use `json.loads` to do the reverse
         
    num = 1
    for stk in enabledList:
        if stk['symbol'] in symbolDict and symbolDict[stk['symbol']]:
            #print("last symbol: %s" % stk['symbol'])
            #print(symbolDict[stk['symbol']])
            comp = symbolDict[stk['symbol']]['company']
            
            # add if only industry is defined
            if (comp['sector']): 
            
                if (stock_us_db.manage_stock(stk['symbol'], stk['name'], comp['description'], comp['sector'], comp['industry'], "NA", comp['exchange'])):
                    print("%s. %s [%s > %s] is added/updated" % (num, stk['symbol'], comp['sector'], comp['industry']))
                    num = num + 1              
                else:
                    print("%s. %s [%s > %s] is added failed" % (num, stk['symbol'], comp['sector'], comp['industry']))

    print("Stocks updated: %s" % num)
    #{"symbol":"AOSL","name":"Alpha and Omega Semiconductor Limited","date":"2018-05-22","isEnabled":true,"type":"cs","iexId":"362"}
    #{"AFSI-A":{"company":{"symbol":"AFSI-A","companyName":"AmTrust Financial Services Inc. Preferred Series A","exchange":"New York Stock Exchange","industry":"Insurance - Property & Casualty","website":"https://www.amtrustfinancial.com","description":"AmTrust Financial Services Inc underwrites and provides property and casualty insurance products, including workers' compensation, commercial automobile, general liability and warranty coverage, in the United States and internationally.","CEO":"Barry D. Zyskind","issueType":"ps","sector":"Financial Services"}}}
    
def main():

    parse_list()


if __name__ == "__main__":
    main()                
              



