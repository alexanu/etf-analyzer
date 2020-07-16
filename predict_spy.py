#! /usr/local/bin/python3

import pandas as pd
import pickle
import sys
from optparse import OptionParser
import numpy as np
from scipy.signal import argrelextrema
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def label_years (data):
    data['Year'] = 0
    cur_index = 0
    previous_date = data.index[0]
    count = 1
    while cur_index < len(data):
        next_date = data.index[cur_index] + np.timedelta64(1, 'Y')
        closest_index = data.index.get_loc(next_date, method="nearest")
        if cur_index == closest_index:
            break
        closest_date = data.index[closest_index]
        data.loc[previous_date:closest_date,'Year'] = count
        previous_date = closest_date
        count += 1
        cur_index = closest_index
    return data

def analyze_extrema(data):

    num_years = max(data['Year'])

    i = 0
    ticker = data.columns[i]

    lo = 1
    hi = 7

    all_top_df = pd.DataFrame()
    all_bot_df = pd.DataFrame()

    total_lo_index = None

    while hi < num_years:

        tmp = data[ (data['Year'] >= lo) & (data['Year'] <= hi)]
        cur = tmp[[ticker]]

        lo_index = data.index.get_loc(cur.index[0], method="nearest")
        hi_index = data.index.get_loc(cur.index[len(cur) - 1], method="nearest")

        if lo == 1:
            total_lo_index = hi_index + 1

        lo += 1
        hi += 1


        local_mins = argrelextrema(cur.values, np.less_equal, order=45)[0]
        local_maxes = argrelextrema(cur.values, np.greater_equal, order=45)[0]

        local_mins += lo_index
        local_maxes += lo_index

        mins = cur.iloc[argrelextrema(cur.values, np.less_equal, order=45)[0]][ticker]
        maxes = cur.iloc[argrelextrema(cur.values, np.greater_equal, order=45)[0]][ticker]

        next_year_start = hi_index + 1
        next_year_end_date = data.index[next_year_start] + np.timedelta64(1, 'Y')
        next_year_end = data.index.get_loc(next_year_end_date, method="nearest")

        mins_regression = LinearRegression()
        mins_regression.fit(pd.DataFrame(local_mins), mins)
        mins_predictions = mins_regression.predict(pd.DataFrame([x for x in range(next_year_start,next_year_end+1)]))

        maxes_regression = LinearRegression()
        maxes_regression.fit(pd.DataFrame(local_maxes), maxes)
        maxes_predictions = maxes_regression.predict(pd.DataFrame([x for x in range(next_year_start,next_year_end+1)]))

        top_df = pd.DataFrame(maxes_predictions)
        top_df.index = data.index[next_year_start:next_year_end+1]
        top_df.columns = [ticker]

        bot_df = pd.DataFrame(mins_predictions)
        bot_df.index = data.index[next_year_start:next_year_end+1]
        bot_df.columns = [ticker]

        all_bot_df = all_bot_df.append(bot_df)
        all_top_df = all_top_df.append(top_df)


    print(all_top_df)
    print(data)
    plt.plot(all_top_df.index, all_top_df['SPY'], 'b')
    plt.plot(all_bot_df.index, all_bot_df['SPY'], 'r')
    plt.plot(data.index[total_lo_index:], data.iloc[total_lo_index:]['SPY'], 'g')
    plt.show()  






def predict():
    version_msg = "%prog 1.0"
    usage_msg = """%prog FILE [OPTIONS]
Predict when to sell stocks (usually SPY) based on linear regression of local extrema points."""

    parser = OptionParser(version=version_msg,
                          usage=usage_msg)
    parser.add_option("-p", "--period",
                      action="store", dest="period", type = "string", default=None,
                      help="valid periods are 1mo, 3mo, 6mo, 1y, 2y, 5y")
    parser.add_option("-i", "--interval",
                      action="store", dest="interval", type = "string", default=None,
                      help="valid periods are 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")

    options, args = parser.parse_args(sys.argv[1:])

    input_period = options.period
    input_interval = options.interval

    if input_period is None or input_interval is None:
        print("missing input period and / or intput interval")
        exit(1)
    if args:
        file_name = sys.argv[1] + "_period" + input_period + "_interval" + input_interval
        opening_prices = pickle.load(open(file_name + "_opening_price.p", "rb"))
    else:
        print("input file missing")
        exit(1)

    opening_prices = label_years(opening_prices)
    analyze_extrema(opening_prices)


if __name__ == '__main__':
    predict()