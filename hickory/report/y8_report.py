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
from hickory.db import stock_mag8_db, stock_us_mag8_db

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
    elif (int(lcp[0]) > 0):
        change_pct = "+" + "%.2f" % float(lcp[:-1]) + "%"
        change_style = "color: green;"
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

def generate(region="HK"):

    locale.setlocale(locale.LC_ALL, '')
    now = datetime.datetime.now()
    
    if (region=="US"):
        stock_us_mag8_db.update_mag8_stocks_entry()    
        stocks = stock_us_mag8_db.get_mag8_stocks()
        stocks_dict = stock_us_mag8_db.get_mag8_stocks_dict(100)
        #print(stocks)
        #print(stocks_dict)

    else:
        stock_mag8_db.update_mag8_stocks_entry()    
        stocks = stock_mag8_db.get_mag8_stocks()
        stocks_dict = stock_mag8_db.get_mag8_stocks_dict(100)

    html = """<html>
    <head>
        <meta charset="UTF-8">
        <title>Gen-Y Sector Screener</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
        <script type="text/javascript" src="https://rawgithub.com/padolsey/jQuery-Plugins/master/sortElements/jquery.sortElements.js"></script>  

        <style>

            .table-condensed, .row {
                font-size: 11px;
            }
            
            .flink {
                 cursor: pointer;
                 color: #337ab7;
                 text-decoration: underline;
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
        <script>
   
          $(document).ready(function() {
            var table = $('table');
            
            $('#1_header, #2_header, #3_header, #4_header, #4a_header, #5_header, #6_header, #7_header, #8_header, #9_header, #10_header, #11_header, #12_header, #13_header, #14_header, #15_header, #17_header, #18_header, #19_header, #20_header, #21_header, #22_header, #23_header')
                .wrapInner('<span title="Sort this column"/>')
                .each(function(){
                    
                    var th = $(this),
                        thIndex = th.index(),
                        inverse = false;
                    
                    th.click(function(){
                        
                        table.find('td').filter(function(){
                            
                            return $(this).index() === thIndex;
                            
                        }).sortElements(function(a, b){
    
                            if( $.text([a]) == $.text([b]) )
                                return 0;
                            if(isNaN($.text([a])) && isNaN($.text([b]))){
                            
                                if (($.text([a]).includes('/') && $.text([b]).includes('/')) 
                                    || ($.text([a]).includes('(') && $.text([b]).includes('('))
                                    || ($.text([a]).includes('days') && $.text([b]).includes('days'))) {
                                
                                    //alert("[" + $.text([a]).split('/')[0].split('(')[0].replace("days", "").replace(/^\s+|\s+$/g, '') + "]")                 
                                    ta = $.text([a]).split('/')[0].split('(')[0].replace("days", "").replace("-", "0").replace(/^\s+|\s+$/g, '')
                                    tb = $.text([b]).split('/')[0].split('(')[0].replace("days", "").replace("-", "0").replace(/^\s+|\s+$/g, '')
                                
                                    return parseFloat(ta) > parseFloat(tb) ? 
                                        inverse ? -1 : 1
                                        : inverse ? 1 : -1;
                                } 

                                if (($.text([a]).includes('M') && $.text([b]).includes('M')) 
                                    || ($.text([a]).includes('B') && $.text([b]).includes('B'))) {
                                
                                    ta = $.text([a]).replace("M", "").replace("B", "").replace("None", "0").replace(/^\s+|\s+$/g, '')
                                    tb = $.text([b]).replace("M", "").replace("B", "").replace("None", "0").replace(/^\s+|\s+$/g, '')
                                    alert("[" + ta + ", " + tb + "]")
                                    return parseInt(ta) > parseInt(tb) ? 
                                        inverse ? -1 : 1
                                        : inverse ? 1 : -1;
                                } 
                                
                                return $.text([a]) > $.text([b]) ? 
                                   inverse ? -1 : 1
                                   : inverse ? 1 : -1;
                            }
                            else{
                                return parseFloat($.text([a])) > parseFloat($.text([b])) ? 
                                  inverse ? -1 : 1
                                  : inverse ? 1 : -1;
                            }
                            
                        }, function(){
                            
                            // parentNode is the element we want to move
                            return this.parentNode; 
                            
                        });
                        
                        inverse = !inverse;
                            
                    });
                        
                });   
          });
          
        </script>         
    </head>
    <body>"""

    html = html + """<div class="container-fluid">
    <h3><img height="40" src="https://www.ytravelblog.com/wp-content/themes/ytravelblog/images/favicon.ico"/>Gen-Y Sector Screener</h3>
    <p style="font-size: 11px">TO: 1.5m+ / MktCap: 0B+<small> (Last updated: """ + now.strftime("%Y-%m-%d %H:%M") + """)</small></p>
        """
    
    stk_html = """<table class="table table-striped table-bordered table-hover table-condensed">
            <tr class="flink">
                <th id="1_header">Code</th><th id="2_header">Name</th><th id="3_header">Last Close</th>
                <th id="4_header">V/AV</th> <th id="4a_header">RoC</th><th id="6_header">PE</th>
                <th id="8_header">1mC%</th><th id="9_header">3mC%</th><th id="10_header">1yC%</th><th id="11_header">1mRS%</th>
                <th id="12_header">3mRS%</th><th id="13_header">1yRS%</th><th id="14_header">MktCap</th><th id="15_header">52WkLH</th>
                <th id="17_header">3mVol</th><th id="18_header">ma30</th>
                <th id="19_header">ma50</th><th id="20_header">ma150</th><th id="21_header">ma200</th><th id="22_header">macd Xup</th><th id="23_header">since</th>
            </tr>

                """

    for stock in stocks:    
        #print(stock["_52WEEK_HIGH"])
        if (stock["_52WEEK_HIGH"] and (stock["LAST_CLOSE"] > stock["_52WEEK_HIGH"])):
            img_sup = "<img src='http://images.emojiterra.com/emojione/v2/512px/1f525.png' width='15' style='vertical-align: top'/>"
        else:
            img_sup = ""


        if (region == "US"):
            surl = "https://finance.google.com/finance?q="
        else:
            surl = "http://aastocks.com/tc/stocks/analysis/company-fundamental/?symbol="

        name_text = "<a href='" + surl + stock["CODE"] + "' target='_blank'>" + stock["stockname"] + "</a>" + img_sup
    
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
                      <td><a name='%s'/><a href="/streaming.html?code=%s" target="_blank">%s</a></td>
                      <td class='text-nowrap'>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td>
                      <td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                  </tr>""" % (stock["CODE"], stock["CODE"], stock["CODE"], name_text, str(stock["LAST_CLOSE"]) + " /" + fpct(lcp).strip(), vol_ratio, "%.2f" % stock["Y8_ROC_MARK"] ,stock["PE"], fnum(stock["_1MONTH_CHANGE"]), fnum(stock["_3MONTH_CHANGE"]), fnum(stock["_52WEEK_CHANGE"]), fnum(stock["_1MONTH_HSI_RELATIVE"]), fnum(stock["_3MONTH_HSI_RELATIVE"]), fnum(stock["_52WEEK_HSI_RELATIVE"]), su.rf2s(stock["MARKET_CAPITAL"]), str(stock["_52WEEK_LOW"]) + " - " + str(stock["_52WEEK_HIGH"]), su.rf2s(stock["_3MONTH_AVG_TURNOVER"]), su.rfNum(stock["_30_DAY_MA"], 2), su.rfNum(stock["_50_DAY_MA"], 2), su.rfNum(stock["_150_DAY_MA"], 2), su.rfNum(stock["_200_DAY_MA"], 2), macd_text, fdaysago(stock["Y8_ENTRY_DATE"]))

        stk_html = stk_html + row_text
 
    stk_html  = stk_html + """</table>"""
    html = html + stk_html  
    html = html + """</div>"""
    html = html + """</body></html>"""

    print("Generating Report ...")
    #print(html)
    soup = BeautifulSoup(html, "html.parser")

    reg = ""
    if (region == "US"):
        reg = "_us"

    text_file = open("/var/www/eggyolk.tech/html/y8%s.html" % reg, "w")
    text_file.write(soup.prettify())
    text_file.close()

    text_file = open("/var/www/eggyolk.tech/html/sector%s.html" % reg, "w")
    text_file.write(soup.prettify())
    text_file.close()


def main():
    
    generate()
    generate("US")

if __name__ == "__main__":
    main() 
