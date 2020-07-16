#! /usr/local/bin/python3

import yfinance as yf
import lxml
import pandas as pd
import numpy as np
import pickle
import sys
from optparse import OptionParser

def clean (data):
    data = data.dropna(axis = 0, how = 'all')
    data = data.dropna(axis = 1)
    data['Day'] = [x for x in range(1,len(data)+1)]
   # data.index = [x for x in range(1,len(data)+1)]
    return data

def generate():

    version_msg = "%prog 1.0"
    usage_msg = """%prog FILE [OPTIONS]
Generate dataframe for stock data. Input a file containing ticker symbols separated by newline character."""

    parser = OptionParser(version=version_msg,
                          usage=usage_msg)
    parser.add_option("-p", "--period",
                      action="store", dest="period", type = "string", default=None,
                      help="valid periods are 1mo, 3mo, 6mo, 1y, 2y, 5y, max")
    parser.add_option("-i", "--interval",
                      action="store", dest="interval", type = "string", default=None,
                      help="valid periods are 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
    parser.add_option("-l", "--limit",
                      action="store", dest="limit", type="int", default=None,
                      help="limit to top holdings in ticker symbol list")

    options, args = parser.parse_args(sys.argv[1:])


    symbols = []

    if args:
        with open(sys.argv[1]) as f:
            additional_symbols = f.read().splitlines()
        if not 'SPY' in additional_symbols:
            additional_symbols.append("SPY")
    else:
        print("input file missing")
        exit(1)

    symbols += additional_symbols

    short_periods = ["1d", "5d", "1mo"]
    valid_periods = short_periods + ["3mo", "6mo", "1y", "2y", "5y", "ytd", "max"]
    input_period = options.period
    if input_period is None:
        print("period missing")
        exit(1)
    if not input_period in valid_periods:
        print("invalid period")
        exit(1)

    intraday_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]
    valid_intervals = intraday_intervals + ["1d", "5d", "1wk", "1mo", "3mo"]
    input_interval = options.interval
    if input_interval is None:
        print("interval missing")
        exit(1)
    elif not input_interval in valid_intervals:
        print("invalid interval")
        exit(1)
    elif input_interval in intraday_intervals and input_period not in short_periods:
        print("intraday data only available up to 1mo")
        exit(1)

    limit = options.limit
    if limit:
        if limit <= 0:
            print("Limit cannot be less than or equal to 0")
            exit(1)
        else:
            l = len(symbols)
            l = min(l, limit)
            symbols = symbols[:l]
            if not 'SPY' in symbols:
                symbols.append("SPY")

    data = yf.download(tickers=symbols, period=input_period, interval=input_interval, actions=False)

    if len(symbols) == 1:
        opening_price = data[['Open']]
        closing_price = data[['Close']]
    else:
        opening_price = data['Open']
        closing_price = data['Close']

    opening_price = clean(opening_price)
    closing_price = clean(closing_price)

    if len(opening_price.columns) == 2:
        opening_price = opening_price.rename(columns={'Open': symbols[0]})
        closing_price = closing_price.rename(columns={'Close': symbols[0]})

    returns = 100 * (opening_price - opening_price.iloc[1]) / opening_price.iloc[1]
    returns['Day'] = [x for x in range(1, len(opening_price) + 1)]

    file_name = sys.argv[1]
    file_1_name = file_name + "_period" + input_period + "_interval" + input_interval + "_opening_price.p"
    file_2_name = file_name + "_period" + input_period + "_interval" + input_interval +"_closing_price.p"
    file_3_name = file_name + "_period" + input_period + "_interval" + input_interval +"_opening_returns.p"
    
    pickle.dump(opening_price, open(file_1_name,"wb"))
    pickle.dump(closing_price, open(file_2_name,"wb"))
    pickle.dump(returns,open(file_3_name,"wb"))

    
if __name__ == '__main__':
    generate()


