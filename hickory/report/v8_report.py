#!/usr/bin/python

import configparser
import os
import urllib.request
import urllib.parse
import sqlite3
import locale
import math
import datetime
from bs4 import BeautifulSoup
from hickory.util import config_loader, stock_util as su
from hickory.crawler.aastocks import stock_quote, stock_info
import traceback
import logging
from hickory.db import stock_mag8_db

config = config_loader.load()
period = "ALL"

def fpct(lcp):
    
    if (not lcp):
        return lcp
    
    if (lcp == "N/A"):
        change_pct = lcp
        change_style = ""
    elif ("+" in lcp):
        change_pct = "+" + "%.2f" % float(lcp[1:-1]) + "%"
        change_style = "color: green;"
    elif ("-" in lcp):
        change_pct = "-" + "%.2f" % float(lcp[1:-1]) + "%"
        change_style = "color: red;"
    else:
        change_pct = "%.2f" % float(lcp[:-1]) + "%"
        change_style = ""

    return "<font style='%s'>%s</font>" % (change_style, change_pct)

def fnum(number):
    
    if (number and su.is_number(number)):
        if (number > 0):
            change_style = "color: green;"
            sign = "+"
        elif (number < 0):
            change_style = "color: red;"
            sign = ""
        else:
            change_style = ""
            sign = ""

        return "<font style = '%s'>%s</font>" % (change_style, sign + "%.2f" % number)
    else:
        return number

def generate():

    locale.setlocale(locale.LC_ALL, '')
    now = datetime.datetime.now()
    
    stocks = stock_mag8_db.get_full_stocks_by_vol()

    html = """<html>
    <head>
        <meta charset="UTF-8">
        <title>V-8 Report</title>
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
    <h3><img height="40" src="http://www.really-learn-english.com/image-files/xletter-v.jpg.pagespeed.ic.Z99fucjP4w.jpg"/>V-8 Report</h3>
    <p style="font-size: 11px">TO: 0m+ / MktCap: 0B+<small> (Last updated: """ + now.strftime("%Y-%m-%d %H:%M") + """)</small></p>
        """
    
    stk_html = """<table class="table table-striped table-bordered table-hover table-condensed">
            <tr>
                <th>Code</th><th>Name</th><th>LC</th><th>LPC</th>
                <th>V/AV</th><th>NAV</th><th>PE</th><th>YIELD</th>
                <th>1mΔ%</th><th>3mΔ%</th><th>1yΔ%</th><th>1mRS%</th>
                <th>3mRS%</th><th>1yRS%</th><th>MktCap</th><th>52WkL</th>
                <th>52WkH</th><th>3mVol</th><th>ma30</th>
                <th>ma50</th><th>ma150</th><th>ma200</th>
            </tr>

                """

    for stock in stocks:    

        if (stock["_52WEEK_HIGH"] and stock["LAST_CLOSE"] > stock["_52WEEK_HIGH"]):
            img_sup = "<img src='http://images.emojiterra.com/emojione/v2/512px/1f525.png' width='15' style='vertical-align: top'/>"
        else:
            img_sup = ""

        name_text = "<a href='http://aastocks.com/tc/stocks/analysis/company-fundamental/?symbol=" + stock["CODE"] + "' target='_blank'>" + stock["stockname"] + "</a>" + img_sup + " (" + stock["INDUSTRY_LV2"] + ")"
    
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
                style_bg = "background-color: PowderBlue;"

            vol_ratio = "x" + "%.1f" % (lvr)

        row_text = ""
        style_bg = ""
 
        try:
            row_text = """<tr style='""" + style_bg + """'>
                      <td><a href="/streaming.html?code=%s" target="_blank">%s</a></td>
                      <td class='text-nowrap'>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td>
                  </tr>""" % (stock["CODE"], stock["CODE"], name_text, stock["LAST_CLOSE"], fpct(lcp), vol_ratio, su.rfNum(stock["NAV"], 2), stock["PE"], stock["YIELD"], fnum(stock["_1MONTH_CHANGE"]), fnum(stock["_3MONTH_CHANGE"]), fnum(stock["_52WEEK_CHANGE"]), fnum(stock["_1MONTH_HSI_RELATIVE"]), fnum(stock["_3MONTH_HSI_RELATIVE"]), fnum(stock["_52WEEK_HSI_RELATIVE"]), su.rf2s(stock["MARKET_CAPITAL"]), stock["_52WEEK_LOW"], stock["_52WEEK_HIGH"], su.rf2s(stock["_3MONTH_AVG_TURNOVER"]), stock["_30_DAY_MA"], stock["_50_DAY_MA"], stock["_150_DAY_MA"], stock["_200_DAY_MA"])

        except:
            logging.error(" Error generating html")
            logging.error(traceback.format_exc())

        stk_html = stk_html + row_text
 
    stk_html  = stk_html + """</table>"""
    html = html + stk_html  
    html = html + """</div>"""
    html = html + """</body></html>"""

    print("Generating Report ...")
    #print(html)
    soup = BeautifulSoup(html, "html.parser")

    text_file = open("/var/www/eggyolk.tech/html/screener.html", "w")
    text_file.write(soup.prettify())
    text_file.close()

def main():
    
    generate()

if __name__ == "__main__":
    main() 
