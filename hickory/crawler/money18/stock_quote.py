#!/usr/bin/python

#from bs4 import BeautifulSoup
import demjson
import requests
import time
import locale
import re
from hickory.db import stock_tech_db, stock_db
from hickory.util import stock_util
#from market_watch.db import market_db

EL = "\n"
DEL = "\n\n"
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

def is_52weekhigh(code):

    code = code.lstrip("0")
    #time.sleep(1.5)
    quote_result = get_hk_stock_quote(code)

    if (float(quote_result["Close"])) > float(quote_result["52WeekHigh"].replace(",","")):
        return True
    else:
        return False
    
def get_hk_stock_quote(code):

    code = code.zfill(5)
    durl = "http://money18.on.cc/js/daily/hk/quote/%s_d.js" % code
    rurl = "http://money18.on.cc/js/real/quote/%s_r.js" % code

    #print(durl)
    #print(rurl)

    #print("Code: [" + code + "]")
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    try:
        r = requests.get(durl, headers=headers, timeout=5)
    except requests.exceptions.Timeout:
        # retry once more
        r = requests.get(durl, headers=headers, timeout=5)

    r.encoding = "big5hkscs"
    html = r.text 

    dd = rd = {}

    if ("DOCTYPE" in html):
        return quote_result
    else:
        s = html.split("=")[1]
        dd = demjson.decode(s)
        #print(dd)

    try:
        r = requests.get(rurl, headers=headers, timeout=5)
    except requests.exceptions.Timeout:
        # retry once more
        r = requests.get(rurl, headers=headers, timeout=5)

    r.encoding = "big5hkscs"
    html = r.text
    if ("DOCTYPE" in html):
        return quote_result
    else:
        s = html.split("=")[1].replace(";", "")
        rd = demjson.decode(s)
        #print(rd)


    # both daily dict and real time dict exists
    if (not dd or not rd):
        return quote_result

    name = dd['name'] + EL + dd['nameChi']
    l_range = rd['dyl'] + ' - ' + rd['dyh']
    l_open = dd['preCPrice']
    l_close = rd['ltp']

    #if float(l_close) == 0:
    l_close = rd['np']

    if "issuedShare" in dd:
        mkt_cap = float(l_close) * float(dd["issuedShare"])
        quote_result['MktCap'] = stock_util.rf2s(mkt_cap) 

    last_update = rd['ltt']

    if l_open and not l_open == "null" and l_close and not float(l_close) == 0:
        change_val_f = float(l_close) - float(l_open)
        
        if (change_val_f > 0):
            pfx = "+"
        else:
            pfx = ""
        change_val = pfx + "%.3f" % (change_val_f)
        change_pct = pfx + ("%.3f" % (change_val_f / float(l_open) * 100)) + "%"
    else:
        change_val = "0.00"
        change_pct = "0.00%"

    volume = stock_util.rf2s(float(rd['vol']))

    f_vol_now = f_vol_avg_3mth = None
    f_vol_now = float(rd['vol'])

    stk = stock_tech_db.get_stock_tech(code)
    #print(stk)
    if (stk and stk["_3MONTH_AVG_VOL"]):
        f_vol_avg_3mth = float(stk["_3MONTH_AVG_VOL"])

    if (f_vol_now and f_vol_avg_3mth):
        quote_result["V2V"] = "%.2f" % (f_vol_now / f_vol_avg_3mth)

    turnover = stock_util.rf2s(float(rd['tvr']))

    pe_ratio = mkt_cap = None

    if (stk and stk["MARKET_CAPITAL"]):
        mkt_cap = stock_util.rf2s(float(stk["MARKET_CAPITAL"])) 
    if (stk and stk["PE"]):
        pe_ratio = stk["PE"]
    
    wk_low = dd['wk52Low']
    wk_high = dd['wk52High']

    dividend = dd['dividend']    

    eps = dd['eps']
    
    quote_result["CodeName"] = name.strip("\r\n")
    quote_result["Close"] = l_close.strip("\r\n")
    quote_result["ChangeVal"] = str(change_val)
    quote_result["ChangePercent"] = change_pct.strip("\r\n")

    if ("+" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "UP"
    elif ("-" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "DOWN"
    else:
        quote_result["Direction"] = "NONE"

    quote_result["Range"] = "L/H " + l_range.strip("\r\n")

    quote_result["Open"] = l_open.strip("\r\n")
    quote_result["Volume"] = str(volume)
    quote_result["LastUpdate"] = last_update.strip("\r\n")

    quote_result["Turnover"] = str(turnover)
    quote_result["PE"] = pe_ratio
    
    if (dividend):
        dividend = "%.2f" % (float(dividend.strip("\r\n")) / float(l_close) * 100) + "%" 
        quote_result["DivRatio"] = dividend.strip("\r\n")
    quote_result["EPS"] = eps

    quote_result["52WeekLow"] = wk_low.strip()
    quote_result["52WeekHigh"] = wk_high.strip()

    quote_result["LotSize"] = dd['lotSize']

    if "cbbcCPrice" in dd and not dd['cbbcCPrice'] == "0.00":
        quote_result["CallPrice"] = dd['cbbcCPrice']

    if "stkPrice" in dd and not dd['stkPrice'] == "0.00":
        quote_result["Strike"] = dd['stkPrice']

    if "usCode" in dd:
        quote_result["Underlying"] = dd['usCode'] 
    elif "uaCode" in dd:
        quote_result["Underlying"] = dd['uaCode']

    if "cnvRatio" in dd and not dd['cnvRatio'] == "0.000":
        quote_result["ConversionRatio"] = dd['cnvRatio']
    
    if "gearing" in dd and not dd['gearing'] == "0.000":
        quote_result["EffGearing"] = dd['gearing']

    if "premium" in dd and not dd['premium'] == "0.000":
        quote_result["Premium"] = dd['premium']

    if "maturity" in dd and not dd['maturity'] == "null":
        quote_result["Expiry"] = dd['maturity'] 
    
    if "relatedStock" in dd and not dd['relatedStock'] == "":
        quote_result["RelatedStock"] = "/qq" + dd['relatedStock'] 
        #print(quote_result["RelatedStock"])   
 
    if "relatedSZStock" in dd and not dd['relatedSZStock'] == "":
        quote_result["RelatedSZStock"] = "/qq" + dd['relatedSZStock'] 

    return quote_result

def get_quote_message(code, simpleMode=True):

    locale.setlocale( locale.LC_ALL, '' )
    passage = ""
    quote_result = {}
    quote_result = get_hk_stock_quote(code)
  
    #print(quote_result)
    if (not quote_result):
        passage = "Result not found for " + code
    else:    

        direction = u'\U0001F539'

        if (quote_result["Direction"] == "UP"):
            direction = u'\U0001F332'
        elif (quote_result["Direction"] == "DOWN"):
            direction = u'\U0001F53B'

        passage = "<b>" + quote_result["CodeName"] + "</b>" + EL
        passage = passage + direction + "" + "$%.3f" % float(quote_result["Close"]) + " (" + quote_result["ChangeVal"] + "/" + quote_result["ChangePercent"] + ")" + EL
        passage = passage + quote_result["Range"] + " (" + quote_result["Volume"] + "/" + quote_result["Turnover"] + ")"+ EL

        icon_v2v = ""
        if ("V2V" in quote_result):
            if (float(quote_result["V2V"]) > 1.5):
                 icon_v2v = u'\U0001F414'
            elif (float(quote_result["V2V"]) > 1.0):
                 icon_v2v = u'\U0001F424'
            passage = passage + icon_v2v +  "V/AV " + "x" + quote_result["V2V"] + EL
      
        if ("52WeekHigh" in quote_result and "52WeekLow" in quote_result): 
            if (not quote_result["52WeekHigh"] == "N/A" and not quote_result["52WeekLow"] == "N/A"):
                if (float(quote_result["Close"])) > float(quote_result["52WeekHigh"].replace(",","")):
                    passage = passage + u'\U0001F525' + "<i>52 Week High</i>" + EL
                elif (float(quote_result["Close"])) < float(quote_result["52WeekLow"].replace(",","")):
                    passage = passage + u'\U00002744' + "<i>52 Week Low</i>" + EL 
        
        if (simpleMode):
            return passage     

        passage = passage + EL 

        attrs = ["Open", "PrevClose", "LotSize", "PE", "Yield", "DivRatio", "EPS", "MktCap", "NAV", "52WeekHigh", "52WeekLow", "Exchange", "ImpVol", "RemainingDays", "Strike", "CallPrice", "SpotVsCall", "EffGearing", "Delta", "Premium", "OutStanding", "Moneyness", "Underlying", "Expiry", "ConversionRatio","RelatedStock","RelatedSZStock", "LastUpdate"]

        for attr in attrs:
            passage = passage + constructPassageAttributes(attr, quote_result)

    return passage

def constructPassageAttributes(key, qDict):
    
    if (key in qDict and not str(qDict[key]) == ""):
        return key + ": " + str(qDict[key]) + EL
    else:
        return ""

def main():

    #quote = get_hk_stock_quote('87001')
    #quote = get_hk_stock_quote('61383')
    #quote = get_hk_stock_quote('12200')
    #quote = get_hk_stock_quote('8366')
    #quote = get_hk_stock_quote('2822')

    #quote = get_hk_stock_quote('87002')
    
    #for key, value in quote.items():
    #    print(key, ":", value)

    #for code in ['136', '6068', '1918', '87001','61383','12200','8366','345']:
    for code in ['11560']:
        print(get_quote_message(code, False))


    for code in ['6','7','8']:
        print(is_52weekhigh(code))

if __name__ == "__main__":
    main()                
              



