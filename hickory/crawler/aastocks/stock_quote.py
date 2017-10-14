#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import locale
import re
from hickory.db import stock_tech_db, stock_db
from hickory.util import stock_util
from hickory.crawler.google import stock_quote as google_stock_quote
from hickory.crawler.money18 import stock_quote as m18_stock_quote
#from market_watch.db import market_db

EL = "\n"
DEL = "\n\n"
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_cn_stock_quote(code):

    url = "http://www.aastocks.com/en/cnhk/quote/detail-quote.aspx?shsymbol=" + code

    #print("URL: [" + url + "]")
    
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
    
    table = soup.find("table", {"id": "tbQuote"})

    if (not table):
        return quote_result

    name = soup.find("span", {"id": "cp_ucStockBar_litInd_StockName"}).text
    cell = table.findAll("tr")[0].findAll("td")[0]
    p_close = cell.findAll("span", {"class": "ss2"})[0].text.replace(",","")
    l_range = cell.findAll("span", {"class": "ss2"})[1].text
    l_open = cell.findAll("span", {"class": "ss2"})[2].text
    l_close = cell.find("div", {"class": "font33"}).text.strip()    

    cell = table.findAll("tr")[0].findAll("td")[1]
    change_val = cell.findAll("div", {"class": "ss3"})[0].text

    cell = table.findAll("tr")[0].findAll("td")[2]
    volume = cell.findAll("div", {"class": "ss3"})[0].text.strip()

    cell = table.findAll("tr", recursive=False)[1].findAll("td")[0]
    change_pct = cell.findAll("div", {"class": "ss3"})[0].text
    #print(table.findAll("tr", recursive=False)[1])
    cell = table.findAll("tr", recursive=False)[1].findAll("td")[1]
    turnover = cell.findAll("div", {"class": "ss3"})[0].text.strip()

    row = table.findAll("tr", recursive=False)[3]
    pe_ratio = row.findAll("td")[0].findAll("div", {"class": "ss2"})[0].text.split("/")[1].strip()
    eps = row.findAll("td")[1].findAll("div", {"class": "ss2"})[0].text.strip()
    
    row = table.findAll("tr", recursive=False)[4]
    yiel = row.findAll("td")[0].findAll("div", {"class": "ss2"})[0].text.split("/")[1].strip()
    dividend = row.findAll("td")[1].findAll("div", {"class": "ss2"})[0].text.strip()

    row = table.findAll("tr", recursive=False)[5]
    nav = row.findAll("td")[0].findAll("div", {"class": "ss2"})[0].text.split("/")[1].strip()

    row = table.findAll("tr", recursive=False)[8]
    lots = row.findAll("td")[0].findAll("div", {"class": "ss2"})[0].text.strip()

    row = table.findAll("tr", recursive=False)[7]
    mkt_cap = row.findAll("td")[0].findAll("div", {"class": "ss2"})[0].text.split("/")[1].strip()
    exchange = row.findAll("td")[1].findAll("div", {"class": "ss2"})[0].text.strip()

    table = soup.find("table", {"id": "tbHist"})
    wk_range = table.findAll("tr")[4].findAll("td")[1].text.strip()
    #print(wk_range)
    divgrid = soup.find("div", {"class": "grid_11"})
    last_update = divgrid.findAll("div", {"class": "content"}, recursive=False)[1].find("span", {"class": "cls"}).text
   
    quote_result["CodeName"] = name

    quote_result["Close"] = l_close
    quote_result["ChangeVal"] = change_val
    quote_result["ChangePercent"] = change_pct

    if ("+" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "UP"
    elif ("-" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "DOWN"
    else:
        quote_result["Direction"] = "NONE"

    quote_result["Range"] = l_range

    quote_result["Open"] = l_open
    quote_result["PrevClose"] = p_close
    quote_result["Volume"] = volume
    quote_result["LastUpdate"] = last_update

    quote_result["LotSize"] = lots
    quote_result["Turnover"] = turnover
    quote_result["PE"] = pe_ratio
    quote_result["Yield"] = yiel
    quote_result["DivRatio"] = dividend
    quote_result["EPS"] = eps
    quote_result["MktCap"] = mkt_cap
    quote_result["NAV"] = nav
    quote_result["Exchange"] = exchange

    quote_result["52WeekLow"] = wk_range.split("-")[0].strip()
    quote_result["52WeekHigh"] = wk_range.split("-")[1].strip()
   
    return quote_result

def get_us_stock_quote(code):

    url = "http://www.aastocks.com/en/usq/quote/quote.aspx?symbol=" + code

    #print("URL: [" + url + "]")
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
    
    table = soup.find("div", {"class": "grid_11"}).find("table", {"class":"tblM"})

    if (not table):
        return quote_result

    name = soup.find("div", {"id": "divSymbol"}).find("span", {"id": "cp_ucUSCurBar_litSymbol"}).text
    cell = table.findAll("tr")[0].findAll("td")[0]
    p_close = cell.findAll("div", {"class": "float_r"})[0].text.split("：")[1].replace(",","")
    div_range = cell.findAll("div", {"style": "height:10px;"})[0]
    l_range = div_range.findAll("b")[0].text.replace(",","") + " - " + div_range.findAll("b")[1].text.replace(",","")
    if (cell.findAll("div", {"id": "cp_pQuoteBar"})):
        l_open = cell.findAll("div", {"id": "cp_pQuoteBar"})[0].findAll("b", {"style": "color:Black"})[0].text.replace(",","")
    else:
        l_open = "N/A"
    l_close = cell.find("div", {"class": "font26"}).text.strip().replace(",","")    

    last_update = cell.find("div", {"class": "rmk2"}).text.strip().replace("(Last Update:", "").replace(")","").strip()

    cell = table.findAll("tr")[0].findAll("td")[1]
    change_val = cell.findAll("div", {"class": "font18"})[0].text

    cell = table.findAll("tr")[0].findAll("td")[2]
    volume = cell.findAll("div", {"class": "font18"})[0].text.strip()
    if ("N/A" in volume):
        turnover = "N/A"
    else: 
        turnover = "%.2f" % (float(volume[:-1]) * float(l_close)) + volume[-1]

    cell = table.findAll("tr", recursive=False)[1].findAll("td")[0]
    change_pct = cell.findAll("div", {"class": "font18"})[0].text

    cell = table.findAll("tr", recursive=False)[1].findAll("td")[1]
    pe_ratio = cell.findAll("div", {"class": "font18"})[0].text.strip()

    row = table.findAll("tr", recursive=False)[2]
    wk_low = row.findAll("td")[0].findAll("div", {"class": "float_r"})[0].text.strip().replace(",","")
    wk_high = row.findAll("td")[1].findAll("div", {"class": "float_r"})[0].text.strip().replace(",","")
    
    row = table.findAll("tr", recursive=False)[3]
    eps = row.findAll("td")[0].findAll("div", {"class": "float_r"})[0].text.strip()
    exchange = row.findAll("td")[1].findAll("div", {"class": "float_r"})[0].text.strip()

    row = table.findAll("tr", recursive=False)[4]
    
    _yield = None
    if ("Yield" in row.findAll("td")[0].text):
        _yield = row.findAll("td")[0].findAll("div", {"class": "float_r"})[0].text.strip()
    
    dividend = None
    if ("Div" in row.findAll("td")[1].text):
        dividend = row.findAll("td")[1].findAll("div", {"class": "float_r"})[0].text.strip()
   
    quote_result["CodeName"] = name
    quote_result["Close"] = l_close
    quote_result["ChangeVal"] = change_val
    quote_result["ChangePercent"] = change_pct

    if ("+" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "UP"
    elif ("-" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "DOWN"
    else:
        quote_result["Direction"] = "NONE"

    quote_result["Range"] = l_range

    quote_result["Open"] = l_open
    quote_result["PrevClose"] = p_close
    quote_result["Volume"] = volume
    quote_result["LastUpdate"] = last_update

    quote_result["Turnover"] = turnover
    quote_result["PE"] = pe_ratio
    
    if (_yield):
        quote_result["Yield"] = _yield 
    if (dividend):
        quote_result["DivRatio"] = dividend
    quote_result["EPS"] = eps

    quote_result["52WeekLow"] = wk_low.strip()
    quote_result["52WeekHigh"] = wk_high.strip()
   
    return quote_result

def is_derivative(code):

    if (not code.isdigit()):
        return False
    else:
        code = code.lstrip("0")
        if (len(code) == 5 and code[0] in ('1','2','6')):
            return True

    return False

def get_stock_quote_derivative(code):

    isCBBC = False
    if (code[0] == '6'):
        isCBBC = True

    url = "http://www.aastocks.com/en/mobile/Quote.aspx?symbol=" + code

    #print("URL: [" + url + "]")
    
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
    
    # if no close result, just return empty
    if (not soup.find("td", {"class": "quote_table_header_text"}).text.strip()):
        return quote_result

    quote_result["CodeName"] = (soup.find("td", {"class": "quote_table_header_text"}).text)

    div_last = soup.find("div", {"class": "text_last"})

    quote_result["Close"] = (div_last.text.strip().replace(",",""))

    td_last = soup.find("td", {"class": "cell_last"})
    quote_result["ChangeVal"] = (td_last.find_all("div")[2].find_all("span")[0].text)
    quote_result["ChangePercent"] = (td_last.find_all("div")[2].find_all("span")[1].text)

    if ("+" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "UP"
    elif ("-" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "DOWN"
    else:
        quote_result["Direction"] = "NONE"

    quote_result["Range"] = (td_last.find_all("div")[3].text.strip())

    td_last = soup.find("td", {"class": "cell_last_height"})
    quote_result["Open"] = (td_last.find_all("td")[2].find("span").text)
    quote_result["Volume"] = (td_last.find_all("td")[3].find("span").text)
    quote_result["Turnover"] = (td_last.find_all("td")[4].find("span").text)

    div_content = soup.find("div", {"id": "ctl00_cphContent_pQuoteDetail"})
    quote_result["LastUpdate"] = (div_content.find("font", {"class": "font12_white"}).text)

    rows = div_content.find_all("table")[0].find_all("tr", recursive=False)

    quote_result[("SpotVsCall" if isCBBC else "ImpVol")] = (rows[2].find_all("td")[0].find("span").text)
    quote_result["Premium"] = (rows[2].find_all("td")[1].find("span").text)
    quote_result["RemainingDays"] = (rows[3].find_all("td")[0].find("span").text)
    quote_result["EffGearing"] = (rows[3].find_all("td")[1].find("span").text)
    quote_result["OutStanding"] = (rows[4].find_all("td")[0].find("span").text)
    quote_result[("CallPrice" if isCBBC else "Delta")] = (rows[4].find_all("td")[1].find("span").text)
    quote_result["LotSize"] = (rows[5].find_all("td")[0].find("span").text)
    quote_result["Strike"] = (rows[5].find_all("td")[1].find("span").text)

    div52 = soup.find("div", {"id": "ctl00_cphContent_pWarrant"})
    
    quote_result["Moneyness"] = div52.find("span", {"class": "moneybar"}).text.strip()
    
    if div52.find("a"):
        quote_result["Underlying"] = "/qd" + div52.find("a").text.strip()
    else:
        quote_result["Underlying"] = div52.findAll("span", {"class", "float_right"})[1].text.strip()
 
    return quote_result

def get_stock_quote(code):

    if(is_derivative(code)):
        return get_stock_quote_derivative(code)

    url = "http://www.aastocks.com/en/mobile/Quote.aspx?symbol=" + code

    #print("URL: [" + url + "]")
    
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
    
    # if no close result, just return empty
    if (not soup.find("td", {"class": "quote_table_header_text"}).text.strip()):
        return quote_result

    quote_result["CodeName"] = (soup.find("td", {"class": "quote_table_header_text"}).text)

    # replace with cname if available
    cname = stock_db.get_stock_name(code)
    if cname:
        quote_result["CodeName"] = quote_result["CodeName"] + '\n' + cname 
 
    div_last = soup.find("div", {"class": "text_last"})

    quote_result["Close"] = (div_last.text.strip().replace(",",""))

    td_last = soup.find("td", {"class": "cell_last"})
    quote_result["ChangeVal"] = (td_last.find_all("div")[2].find_all("span")[0].text)
    quote_result["ChangePercent"] = (td_last.find_all("div")[2].find_all("span")[1].text)

    if ("+" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "UP"
    elif ("-" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "DOWN"
    else:
        quote_result["Direction"] = "NONE"

    quote_result["Range"] = (td_last.find_all("div")[3].text.strip())

    td_last = soup.find("td", {"class": "cell_last_height"})
    quote_result["Open"] = (td_last.find_all("td")[2].find("span").text)
    quote_result["PrevClose"] = (td_last.find_all("td")[3].find("span").text)
    quote_result["Volume"] = (td_last.find_all("td")[4].find("span").text)

    f_vol_now = f_vol_avg_3mth = None

    if (stock_util.rf(quote_result["Volume"])):
        f_vol_now = float(stock_util.rf(quote_result["Volume"]))
    
    stk = stock_tech_db.get_stock_tech(code)
    #print(stk)
    if (stk and stk["_3MONTH_AVG_VOL"]):
        f_vol_avg_3mth = float(stk["_3MONTH_AVG_VOL"])

    if (f_vol_now and f_vol_avg_3mth):
        quote_result["V2V"] = "%.2f" % (f_vol_now / f_vol_avg_3mth)

    #quote_result[""] = (soup.find("div", {"class": "ctl00_cphContent_pQuoteDetail"}))
    div_content = soup.find("div", {"id": "ctl00_cphContent_pQuoteDetail"})
    quote_result["LastUpdate"] = (div_content.find("font", {"class": "font12_white"}).text)

    rows = div_content.find_all("table")[0].find_all("tr", recursive=False)

    quote_result["LotSize"] = (rows[2].find_all("td")[0].find("span").text)
    quote_result["Turnover"] = (rows[2].find_all("td")[1].find("span").text)
    quote_result["PE"] = (rows[3].find_all("td")[0].find("span").text)
    quote_result["Yield"] = (rows[3].find_all("td")[1].find("span").text)
    quote_result["DivRatio"] = (rows[4].find_all("td")[0].find("span").text)
    quote_result["EPS"] = (rows[4].find_all("td")[1].find("span").text)
    quote_result["MktCap"] = (rows[5].find_all("td")[0].find("span").text)
    quote_result["NAV"] = (rows[5].find_all("td")[1].find("span").text)

    div52 = soup.find("div", {"id": "ctl00_cphContent_p52Week"})
    
    if (div52.find("span").text == "N/A"):
        quote_result["52WeekLow"] = "N/A"
        quote_result["52WeekHigh"] = "N/A"
    else:
        quote_result["52WeekLow"] = (div52.find("span").text.split("-")[0].strip())
        quote_result["52WeekHigh"] = (div52.find("span").text.split("-")[1].strip())
    
    return quote_result

def get_quote_message(code, region="HK", simpleMode=True):

    locale.setlocale( locale.LC_ALL, '' )
    passage = ""
    isGoogle = True
    
    if (region == "HK"):
        quote_result = m18_stock_quote.get_hk_stock_quote(code)
        quote_result["CompanyProfile"] = "/qS" + code
    elif (region == "CN"):
        quote_result = get_cn_stock_quote(code)
    elif (region == "US"):
        try:
            quote_result = google_stock_quote.get_us_stock_quote(code)
        except:
            quote_result = get_us_stock_quote(code)
            isGoogle = False
    
    #print(quote_result)
    if (not quote_result):
        passage = "Result not found for " + code
    else:    

        direction = u'\U0001F539'

        if (quote_result["Direction"] == "UP"):
            direction = u'\U0001F332'
        elif (quote_result["Direction"] == "DOWN"):
            direction = u'\U0001F53B'

        passage = "<b>" + quote_result["CodeName"] + "</b>" + " (" + code + ")" + EL
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
                if (region == "US" and isGoogle):
                    if (float(quote_result["Range"].split("-")[1])) >= float(quote_result["52WeekHigh"].replace(",","")):
                        passage = passage + u'\U0001F525' + "<i>52 Week High</i>" + EL
                    elif (float(quote_result["Range"].split("-")[1])) <= float(quote_result["52WeekLow"].replace(",","")):
                        passage = passage + u'\U00002744' + "<i>52 Week Low</i>" + EL 
                else:
                    if (float(quote_result["Close"])) > float(quote_result["52WeekHigh"].replace(",","")):
                        passage = passage + u'\U0001F525' + "<i>52 Week High</i>" + EL
                    elif (float(quote_result["Close"])) < float(quote_result["52WeekLow"].replace(",","")):
                        passage = passage + u'\U00002744' + "<i>52 Week Low</i>" + EL 
        
        if (simpleMode):
            return passage     

        passage = passage + EL 

        attrs = ["Open", "PrevClose", "LotSize", "PE", "Yield", "DivRatio", "EPS", "MktCap", "NAV", "52WeekHigh", "52WeekLow", "Exchange", "ImpVol", "RemainingDays", "Strike", "CallPrice", "SpotVsCall", "EffGearing", "Delta", "Premium", "OutStanding", "Moneyness", "Underlying", "Expiry", "ConversionRatio", "CompanyProfile", "RelatedStock", "RelatedSZStock", "Shares", "Beta", "LastUpdate"]

        for attr in attrs:
            passage = passage + constructPassageAttributes(attr, quote_result)

    return passage

def constructPassageAttributes(key, qDict):

    if (key in qDict and not str(qDict[key]) == ""):
        return key + ": " + str(qDict[key]) + EL
    else:
        return ""

def main():

    quote = get_us_stock_quote('HEES')
    #quote = get_cn_stock_quote('000001')
    #quote = get_stock_quote('3054')
    for key, value in quote.items():
        print(key, ":", value)
    #print(get_stock_quote_derivative('28497'))
    #print(get_stock_quote_derivative('60002'))
    #print(get_quote_message('28497', "HK", False))
    #print(get_quote_message('60002', "HK", False))
    #print(get_quote_message('000001',"CN", False))
 
    print(get_quote_message('136',"HK", False))
    print(get_quote_message('MSFT',"US", False))
    print(get_quote_message('AMZN',"US", False))

if __name__ == "__main__":
    main()                
              



