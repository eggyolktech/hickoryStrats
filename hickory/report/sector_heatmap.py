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
from hickory.db import stock_sector_db

config = config_loader.load()
period = "ALL"

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

def fnum(number):
    
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

        return "<font style = '%s'>%s</font>" % (change_style, sign + "%.2f" % number)

    return number

def generate():

    locale.setlocale(locale.LC_ALL, '')
    now = datetime.datetime.now()
    
    industries = stock_sector_db.get_hot_industries(period)

    html = """<html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="300">        
        <title>Sector Heatmap</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
        <script>
            
            $(document).ready(function(){
            
                if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                    $("div[class='col-sm-3']").toggleClass('col-sm-3 col-sm-6');
                }
            });
            
            function on(layer) {
                document.getElementById("overlay" + layer).style.display = "block";
            }

        </script>

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
    <h3><img height="40" src="https://s.w.org/images/core/emoji/2.3/svg/1f413.svg"/>Sector Heatmap</h3>
    <p style="font-size: 11px">TO: 20m+ / MktCap: 2B+ / RS: """ + period + """<small> (Last updated: """ + now.strftime("%Y-%m-%d %H:%M") + """)</small></p>
        """
    num_rows = math.ceil(len(industries) / 4)

    for i in range(0, num_rows):
        html = html + """<div class="row">"""

        for j in range (0, 4):
            if (i*4 + j < len(industries)):
                # determine background color
                bgcolor = "lavender"
                if (j%2 == 1):
                    bgcolor = "lavenderblush"

                html = html + """<div class="col-sm-3" style="background-color:""" + bgcolor + """;">"""
                
                # if industry found
                if (i*4 + j < len(industries)):
                    stocks = stock_sector_db.get_hot_stocks_by_industry(industries[i*4 + j], period)
                    html = html + ("""<h6><b><a href="#" onclick="on('%s')">%s</a></b> (%s)</h6>""" % (industries[i*4 + j], industries[i*4 + j], len(stocks)))

                    # get industry stock list
                    stk_html = """<table class="table table-striped table-bordered table-hover table-condensed">"""
                    stk_overlay_html = """<table class="table bg-info table-condensed">
                                    <tr>
                                        <th>Code</th><th>Name</th><th>LC</th><th>LPC</th>
                                        <th>V/AV</th><th>NAV</th><th>PE</th><th>YIELD</th>
                                        <th>1mΔ%</th><th>3mΔ%</th><th>1yΔ%</th><th>1mRS%</th>
                                        <th>3mRS%</th><th>1yRS%</th><th>MktCap</th><th>52WkH</th>
                                        <th>52WkLow</th><th>1mVol</th><th>3mVol</th><th>ma10</th>
                                        <th>ma50</th><th>ma90</th><th>ma250</th><th>rsi14</th>
                                    </tr>"""
                    #print(len(stock_sector_db.get_hot_stocks_by_industry(industries[i*4 + j], period)))
                    for stock in stocks:
                        #print(stock)
                        #print(stock["code"]) 
                        lcp = stock["LAST_CHANGE_PCT"]
                        lvr = stock["LAST_VOL_RATIO"]
                         
                        style_bg = ""
                        vol_ratio = "-"
                        if (lvr):
                            if (float(lvr) > 5):
                                style_bg = "background-color: yellow;" 
                            elif (float(lvr) > 1.5):
                                style_bg = "background-color: LawnGreen;"
                            elif (float(lvr) > 1.0):
                                style_bg = "background-color: PowderBlue;"

                            vol_ratio = "x" + "%.1f" % (lvr)
                        

                        if (stock["LAST_CLOSE"] > stock["_52WEEK_HIGH"]):
                            img_sup = "<img src='http://images.emojiterra.com/emojione/v2/512px/1f525.png' width='15' style='vertical-align: top'/>"
                        else:
                            img_sup = ""
 
                        name_text = "<a href='http://aastocks.com/tc/stocks/analysis/company-fundamental/?symbol=" + stock["code"] + "' target='_blank'>" + stock["name"] + "</a>" + img_sup
                        row_text = """<tr style='""" + style_bg + """'>
                                        <td><a href="/streaming.html?code=%s" target="_blank">%s</a></td>
                                        <td>%s</td><td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        </tr>""" % (stock["code"], stock["code"], name_text, stock["LAST_CLOSE"], fpct(lcp), vol_ratio)
                        stk_html = stk_html + row_text

                        row_text_overlay = """<tr style='""" + style_bg + """'>
                                        <td><a href="/streaming.html?code=%s" target="_blank">%s</a></td>
                                        <td class='text-nowrap'>%s</td><td>%s</td><td>%s</td>
                                        <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                        <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                        <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                        <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                        <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                        </tr>""" % (stock["code"], stock["code"],  stock["name"], stock["LAST_CLOSE"], fpct(lcp), vol_ratio, stock["NAV"], stock["PE"], stock["YIELD"], fnum(stock["_1MONTH_CHANGE"]), fnum(stock["_3MONTH_CHANGE"]), fnum(stock["_52WEEK_CHANGE"]), fnum(stock["_1MONTH_HSI_RELATIVE"]), fnum(stock["_3MONTH_HSI_RELATIVE"]), fnum(stock["_52WEEK_HSI_RELATIVE"]), su.rf2s(stock["MARKET_CAPITAL"]), stock["_52WEEK_HIGH"], stock["_52WEEK_LOW"], su.rf2s(stock["_1MONTH_AVG_VOL"]), su.rf2s(stock["_3MONTH_AVG_VOL"]), stock["_10_DAY_MA"], stock["_50_DAY_MA"], stock["_90_DAY_MA"], stock["_250_DAY_MA"], stock["_14_DAY_RSI"])

                        stk_overlay_html = stk_overlay_html + row_text_overlay
 
                    stk_html  = stk_html + """</table>"""
                    stk_overlay_html = stk_overlay_html + """</table>"""
                    html = html + stk_html + """<div id="%s" class="overlay" onclick="javascript: this.style.display = 'none'"><div id="text">""" % ("overlay" + industries[i*4 + j]) + stk_overlay_html + """</div></div>""" 


                html = html + """</div>"""

        html = html + """</div>"""
    
    html = html + """</div>"""
    html = html + """</body></html>"""

    print("Generating Report ...")
    #print(html)
    soup = BeautifulSoup(html, "html.parser")

    text_file = open("/var/www/eggyolk.tech/html/heatmap.html", "w")
    text_file.write(soup.prettify())
    text_file.close()

def main():
    
    generate()

if __name__ == "__main__":
    main() 
