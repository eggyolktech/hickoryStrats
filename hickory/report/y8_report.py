#!/usr/bin/python

import configparser
import os
import urllib.request
import urllib.parse
import sqlite3
import locale
import math
import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
from hickory.util import config_loader, stock_util as su
from hickory.crawler.aastocks import stock_quote, stock_info
from hickory.db import stock_mag8_db

config = config_loader.load()
period = "ALL"

def fdaysago(dateStr):

    then = datetime.datetime.strptime(dateStr, "%Y%m%d").date()
    #then = datetime.datetime.combine(mydate, datetime.time.min)
    now = datetime.datetime.now().date()
    difference =  (now - then) / timedelta(days=1)

    return ('%.0f' % difference) + " days"

def fpct(lcp):
    
    if (not lcp):
        return lcp

    if ("+" in lcp):
        change_pct = "+" + "%.2f" % float(lcp[1:-1]) + "%"
        change_style = "color: green;"
    elif ("-" in lcp):
        change_pct = "-" + "%.2f" % float(lcp[1:-1]) + "%"
        change_style = "color: red;"
    else:
        change_pct = "%.2f" % float(lcp[:-1]) + "%"
        change_style = ""

    return "<font style='%s'>%s</font>" % (change_style, change_pct)

def fnum(number, numdigit="2"):
    
    if (number):
        if (number > 0):
            change_style = "color: green;"
            sign = "+"
        elif (number < 0):
            change_style = "color: red;"
            sign = ""
        else:
            change_style = ""
            sign = ""

        return "<font style = '%s'>%s</font>" % (change_style, sign + ("%." + numdigit + "f") % number)

    return number

def generate():

    locale.setlocale(locale.LC_ALL, '')
    now = datetime.datetime.now()
    
    stock_mag8_db.update_mag8_stocks_entry()    
    stocks = stock_mag8_db.get_mag8_stocks()

    html = """<html>
    <head>
        <meta charset="UTF-8">
        <title>Gen-Y Sector Screener</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

        <style>

            .table-condensed, .row {
                font-size: 11px;
            }
            
            .overlay {
                position: fixed;
                display: none;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0,0,0,0.5);
                z-index: 2;
                cursor: pointer;
            }

            #text{
                position: absolute;
                top: 50%;
                left: 50%;
                font-size: 50px;
                color: white;
                transform: translate(-50%,-50%);
                -ms-transform: translate(-50%,-50%);
            }
            
        </style>
    </head>
    <body>"""

    html = html + """<div class="container-fluid">
    <h3><img height="40" src="https://www.ytravelblog.com/wp-content/themes/ytravelblog/images/favicon.ico"/>Gen-Y Sector Screener</h3>
    <p style="font-size: 11px">TO: 3m+ / MktCap: 0B+<small> (Last updated: """ + now.strftime("%Y-%m-%d %H:%M") + """)</small></p>
        """
    
    stk_html = """<table class="table table-striped table-bordered table-hover table-condensed">
            <tr>
                <th>Code</th><th>Name</th><th>Last Close</th>
                <th>V/AV</th><th>NAV</th><th>PE</th><th>YIELD</th>
                <th>1mΔ%</th><th>3mΔ%</th><th>1yΔ%</th><th>1mRS%</th>
                <th>3mRS%</th><th>1yRS%</th><th>MktCap</th><th>52WkL</th>
                <th>52WkH</th><th>3mVol</th><th>ma30</th>
                <th>ma50</th><th>ma150</th><th>ma200</th><th>macd Xup</th><th>since</th>
            </tr>

                """

    for stock in stocks:    

        if (stock["LAST_CLOSE"] > stock["_52WEEK_HIGH"]):
            img_sup = "<img src='http://images.emojiterra.com/emojione/v2/512px/1f525.png' width='15' style='vertical-align: top'/>"
        else:
            img_sup = ""

        name_text = "<a href='http://aastocks.com/tc/stocks/analysis/company-fundamental/?symbol=" + stock["CODE"] + "' target='_blank'>" + stock["stockname"] + "</a>" + img_sup
    
        lcp = stock["LAST_CHANGE_PCT"]
        lvr = stock["LAST_VOL_RATIO"]

        vol_ratio = "-"
        style_bg = ""

        if(lvr):
            if (float(lvr) > 5):
                style_bg = "background-color: yellow;"
            elif (float(lvr) > 1.5):
                style_bg = "background-color: LawnGreen;"
            elif (float(lvr) > 1.0):
                style_bg = ""
                #style_bg = "background-color: PowderBlue;"

        vol_ratio = "x" + "%.1f" % (lvr)

        macd_text = "-"
        macd_div = stock["MACD_DIVERGENCE"]

        if (macd_div):
            macd_div = fnum(macd_div, "3")
        else:
            macd_div = "-"

        if (stock["MACD_X_OVER_DATE"] and not stock["MACD_X_OVER_DATE"] == "-"):
            macd_text = fdaysago(stock["MACD_X_OVER_DATE"]) + " (" + macd_div + ")"
        else:
            macd_text = macd_text + " (" + macd_div + ")"
        row_text = """<tr style='""" + style_bg + """'>
                      <td><a href="/streaming.html?code=%s" target="_blank">%s</a></td>
                      <td class='text-nowrap'>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                  </tr>""" % (stock["CODE"], stock["CODE"], name_text, str(stock["LAST_CLOSE"]) + " /" + fpct(lcp).strip(), vol_ratio, "%.2f" % stock["NAV"], stock["PE"], stock["YIELD"], fnum(stock["_1MONTH_CHANGE"]), fnum(stock["_3MONTH_CHANGE"]), fnum(stock["_52WEEK_CHANGE"]), fnum(stock["_1MONTH_HSI_RELATIVE"]), fnum(stock["_3MONTH_HSI_RELATIVE"]), fnum(stock["_52WEEK_HSI_RELATIVE"]), su.rf2s(stock["MARKET_CAPITAL"]), stock["_52WEEK_LOW"], stock["_52WEEK_HIGH"], su.rf2s(stock["_3MONTH_AVG_TURNOVER"]), stock["_30_DAY_MA"], stock["_50_DAY_MA"], stock["_150_DAY_MA"], stock["_200_DAY_MA"], macd_text, fdaysago(stock["Y8_ENTRY_DATE"]))

        stk_html = stk_html + row_text
 
    stk_html  = stk_html + """</table>"""
    html = html + stk_html  
    html = html + """</div>"""
    html = html + """</body></html>"""

    print("Generating Report ...")
    #print(html)
    soup = BeautifulSoup(html, "html.parser")

    text_file = open("/var/www/eggyolk.tech/html/y8.html", "w")
    text_file.write(soup.prettify())
    text_file.close()

    text_file = open("/var/www/eggyolk.tech/html/sector.html", "w")
    text_file.write(soup.prettify())
    text_file.close()


def main():
    
    generate()

if __name__ == "__main__":
    main() 
