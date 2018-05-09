
#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import locale
import json
import re
from hickory.util import stock_util
from datetime import datetime

EL = "\n"
DEL = "\n\n"
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_cn_stock_quote(code):
   
   quote_result = {}
   return quote_result

def get_us_stock_quote(code):

    code = code.upper().strip()
    url = "https://api.iextrading.com/1.0/stock/market/batch?symbols=%s&types=quote,stats" % code

    print("URL: [" + url + "]")
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    jsondata = r.text 
    data = json.loads(jsondata)
    #print(data)
    
    if (not code in data):
        return quote_result
        
    quote_obj = data[code]["quote"]
    stats_obj = data[code]["stats"]

    name = quote_obj["companyName"]
    
    l_range = str("%.2f - %.2f " % (quote_obj["low"], quote_obj["high"]))
    l_open = str(quote_obj["open"])
    l_close = str(quote_obj["close"])
    l_close = str(quote_obj["iexRealtimePrice"])

    last_update = str(datetime.fromtimestamp(quote_obj["latestUpdate"]/1000.0).strftime('%Y-%m-%d %H:%M:%S'))

    change_val = str(quote_obj["change"])
    change_pct = ("%.2f" % (quote_obj["changePercent"]*100)) + "%"
    
    volume = str(quote_obj["latestVolume"])
    mean_vol = str(quote_obj["avgTotalVolume"])

    if (mean_vol):
        f_vol_now = stock_util.rf(volume)
        f_vol_avg = stock_util.rf(mean_vol)
        quote_result["V2V"] = "%.2f" % (float(f_vol_now) / float(f_vol_avg))

    if ("0.00" in volume):
        turnover = "N/A"
        quote_result["Volume"] = volume
        quote_result["Turnover"] = turnover
    else:
        turnover = "%.2f" % (float(volume) * float(l_close))
        quote_result["Volume"] = stock_util.rf2s(float(volume.strip("\r\n")))
        quote_result["Turnover"] = stock_util.rf2s(float(turnover))

    mkt_cap = stock_util.rf2s(quote_obj["marketCap"])
    pe_ratio = quote_obj["peRatio"]
    
    wk_low = quote_obj["week52Low"]
    wk_high = quote_obj["week52High"]

    dividend = stats_obj["dividendRate"]
    _yield = stats_obj["dividendYield"]
    
    #print("div %s, yield %s" % (dividend, _yield))

    eps = stats_obj["ttmEPS"]
    shares = stats_obj["sharesOutstanding"]
    beta = stats_obj["beta"]
        
    quote_result["CodeName"] = name
    quote_result["Close"] = l_close
    quote_result["ChangeVal"] = change_val
    quote_result["ChangePercent"] = change_pct

    if ("-" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "DOWN"
    elif (quote_result["ChangeVal"] == "0"):
        quote_result["Direction"] = "NONE"
    else:
        quote_result["Direction"] = "UP"
        quote_result["ChangeVal"] = "+" + quote_result["ChangeVal"]
        quote_result["ChangePercent"] = "+" + quote_result["ChangePercent"]
    
    quote_result["MktCap"] = mkt_cap

    quote_result["Range"] = l_range

    quote_result["Open"] = l_open

    quote_result["LastUpdate"] = last_update

    quote_result["PE"] = pe_ratio
    
    if (_yield):
        quote_result["Yield"] = _yield
    if (dividend):
        quote_result["DivRatio"] = dividend
    quote_result["EPS"] = eps
    quote_result["Shares"] = shares
    quote_result["Beta"] = beta

    quote_result["52WeekLow"] = wk_low
    quote_result["52WeekHigh"] = wk_high
   
    return quote_result

def get_quote_message(code, region="US", simpleMode=True):

    locale.setlocale( locale.LC_ALL, '' )
    passage = ""
    
    quote_result = get_us_stock_quote(code)
    
    #print(quote_result)
    if (not quote_result):
        passage = "Result not found for " + code
    else:    

        direction = u'\U0001F539'

        if (quote_result["Direction"] == "UP"):
            direction = u'\U0001F332'
        elif (quote_result["Direction"] == "DOWN"):
            direction = u'\U0001F53B'

        passage = "<b>" + quote_result["CodeName"] + "</b>" + " (" + code.upper() + ")" + EL
        passage = passage + direction + "" + "$%.3f" % float(quote_result["Close"]) + " (" + quote_result["ChangeVal"] + "/" + quote_result["ChangePercent"] + ")" + EL
        passage = passage + "$" + quote_result["Range"].replace("- ", "- $") + " (" + quote_result["Volume"] + "/" + quote_result["Turnover"] + ")"+ EL

        icon_v2v = ""
        if ("V2V" in quote_result):
            if (float(quote_result["V2V"]) > 1.5):
                 icon_v2v = u'\U0001F414'
            elif (float(quote_result["V2V"]) > 1.0):
                 icon_v2v = u'\U0001F424'
            passage = passage + icon_v2v +  "V/AV " + "x" + quote_result["V2V"] + EL
      
        if ("52WeekHigh" in quote_result and "52WeekLow" in quote_result): 
            if (not quote_result["52WeekHigh"] == "N/A" and not quote_result["52WeekLow"] == "N/A"):
                if (region == "US"):
                    print(quote_result["Range"])
                    print(quote_result["Range"].split("-")[1].replace(",",""))
                    if (quote_result["Range"].strip() == "-"):
                        print("Range is empty")
                    elif (float(quote_result["Range"].split("-")[1].replace(",",""))) >= float(quote_result["52WeekHigh"]):
                        passage = passage + u'\U0001F525' + "<i>52 Week High</i>" + EL
                    elif (float(quote_result["Range"].split("-")[1].replace(",",""))) <= float(quote_result["52WeekLow"]):
                        passage = passage + u'\U00002744' + "<i>52 Week Low</i>" + EL 
                else:
                    if (float(quote_result["Close"])) > float(quote_result["52WeekHigh"]):
                        passage = passage + u'\U0001F525' + "<i>52 Week High</i>" + EL
                    elif (float(quote_result["Close"])) < float(quote_result["52WeekLow"]):
                        passage = passage + u'\U00002744' + "<i>52 Week Low</i>" + EL 
        
        if (simpleMode):
            return passage     

        passage = passage + EL 

        attrs = ["Open", "PrevClose", "LotSize", "PE", "Yield", "DivRatio", "EPS", "MktCap", "NAV", "52WeekHigh", "52WeekLow", "Exchange", "ImpVol", "RemainingDays", "Strike", "CallPrice", "SpotVsCall", "EffGearing", "Delta", "Premium", "OutStanding", "Moneyness", "Underlying", "Expiry", "ConversionRatio", "CompanyProfile", "RelatedStock", "RelatedSZStock", "Shares", "Beta", "LastUpdate"]

        for attr in attrs:
            passage = passage + constructPassageAttributes(attr, quote_result)

    return passage

def constructPassageAttributes(key, qDict):

    if (key in qDict):
        return key + ": " + str(qDict[key]) + EL
    else:
        return ""

def main():

    #quote = get_us_stock_quote('AAPL')
    #quote = get_us_stock_quote('DFT')
    #for key, value in quote.items():
    #    print(key, ":", value)
    print(get_quote_message('GOOG',"US", False))
    print(get_quote_message('ANET',"US", False))
    #print(get_quote_message('SNAP',"US", True))
    #print(get_quote_message('AMZN',"US", False))

    #print(get_quote_message('BRK.B',"US", False))



if __name__ == "__main__":
    main()                
              



