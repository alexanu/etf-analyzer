#! /usr/local/bin/python3

import pandas as pd
import numpy as np
import pickle
import sys
from optparse import OptionParser


def compute_metrics(opening_prices, average, high, low):
    last_day_price = opening_prices.tail(1)
    last_day_price = last_day_price.transpose()
    last_day_price.columns = ["current_price"]
    if average:
        last_days = opening_prices.iloc[len(opening_prices) - average:,]
        last_days_average = last_days.mean(axis=0)
        last_day_price = last_day_price.merge(last_days_average.rename("moving_avg"), left_index=True, right_index=True)
        last_day_price['moving_avg_pct'] = 100 * \
            (last_day_price['current_price'] - last_day_price['moving_avg']) / last_day_price['current_price']
        last_day_price = last_day_price.sort_values(by=['moving_avg_pct'])
    if high:
        maxes = opening_prices.max(axis=0)
        last_day_price['max_price'] = maxes
        last_day_price['max_price_pct'] = 100 * \
            (last_day_price['current_price'] - last_day_price['max_price']) / last_day_price['current_price']
        if not average:
            last_day_price = last_day_price.sort_values(by=['max_price_pct'])
    if low:
        mins = opening_prices.min(axis=0)
        last_day_price['min_price'] = mins
        last_day_price['min_price_pct'] = 100 * \
            (last_day_price['current_price'] - last_day_price['min_price']) / last_day_price['current_price']
        if not average and not high:
            last_day_price = last_day_price.sort_values(by=['min_price_pct'])
    return last_day_price

def screen():
    version_msg = "%prog 1.0"
    usage_msg = """%prog FILE [OPTIONS]
    Rank watchlist stocks based on moving average, peaks, lows, momentum."""

    parser = OptionParser(version=version_msg,
                          usage=usage_msg)
    parser.add_option("-p", "--period",
                      action="store", dest="period", type="string", default=None,
                      help="valid periods are 1mo, 3mo, 6mo, 1y, 2y, 5y")
    parser.add_option("-i", "--interval",
                      action="store", dest="interval", type="string", default=None,
                      help="valid intervals are 1d")
    parser.add_option("-a", "--average",
                      action="store", dest="average", type="int", default=None,
                      help="valid moving average (in days)")
    parser.add_option("-m", "--high",
                      action="store_true", dest="high", default=False,
                      help="highest price in period")
    parser.add_option("-l", "--low",
                      action="store_true", dest="low", default=False,
                      help="lowest price in period")
    parser.add_option("-o", "--open",
                      action="store_true", dest="open", default=False,
                      help="use opening price")

    options, args = parser.parse_args(sys.argv[1:])

    input_period = options.period
    input_interval = options.interval

    valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    valid_intervals = ["1d"]

    if input_period is None or input_interval is None:
        print("missing input period and / or intput interval")
        exit(1)
    elif input_period not in valid_periods or input_interval not in valid_intervals:
        print("you entered either a non-valid period or a non-valid interval")
        exit(1)

    if args:
        file_name = sys.argv[1] + "_period" + input_period + "_interval" + input_interval
        opening_prices = pickle.load(open(file_name + "_opening_price.p", "rb"))
        closing_prices = pickle.load(open(file_name + "_closing_price.p", "rb"))
        returns = pickle.load(open(file_name + "_opening_returns.p", "rb"))
    else:
        print("input file missing")
        exit(1)


    if options.open:
        prices = opening_prices
    else:
        prices = closing_prices

    average = options.average
    if average is None or average <= len(prices):
        prices = compute_metrics(prices, average, options.high, options.low)
    else:
        print("the window you entered is greater than the history of data!")
        exit(1)

    print(prices)


if __name__ == '__main__':
    screen()


