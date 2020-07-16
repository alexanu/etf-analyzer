#! /usr/local/bin/python3

# run like this:  python3 ../visualize_stocks.py sap.txt -p max -i 1d

import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import numpy as np
import seaborn as sns
import sys
from optparse import OptionParser

def get_relative (returns, ref="SPY"):
    return returns.sub(returns['SPY'], axis = 0)

def plot_nine_stocks (data, num = 1, method = None, extrema = None):
    fig = plt.figure(num, figsize=(10,10))
    for i in range(0, min(9, len(data.columns)) ):
        ticker = data.columns[i]
        if ticker == 'Day':
            continue
        ax = fig.add_subplot(3, 3, i+1)
        ax.set_title(ticker)
        if method == "residuals":
            reg = LinearRegression()
            cur = data.iloc[:,i]
            ref = data[['SPY']]
            reg.fit(ref, cur)
            predictions = reg.predict(ref)
            ax.plot(data.index, cur - predictions)
            plt.suptitle('Residuals')
        elif method == "relative":
            cur = data.iloc[:,i]
            ref = data['SPY']
            ax.plot(data.index, cur - ref)
            plt.suptitle('Relative')
        else:
            ax.plot(data['Day'], data.iloc[:,i])
            plt.suptitle('Price')
        if extrema:
            cur = data.iloc[:,[i]]
            cur['min'] = cur.iloc[argrelextrema(cur.values, np.less_equal, order=extrema)[0]][ticker]
            cur['max'] = cur.iloc[argrelextrema(cur.values, np.greater_equal, order=extrema)[0]][ticker]
            bottom_index = data.index[pd.isna(cur['min'])==False]
            min_values = cur['min'][pd.isna(cur['min'])==False]
            top_index = data.index[pd.isna(cur['max'])==False]
            top_values = cur['max'][pd.isna(cur['max'])==False]
            b_reg = LinearRegression()
            b_reg.fit(pd.DataFrame(bottom_index), min_values)
            b_predictions = b_reg.predict(pd.DataFrame(data.index))
            t_reg = LinearRegression()
            t_reg.fit(pd.DataFrame(top_index), top_values)
            t_predictions = t_reg.predict(pd.DataFrame(data.index))
            ax.scatter(data.index, cur['min'], c='r')
            ax.scatter(data.index, cur['max'], c='g')
            ax.plot(data.index, b_predictions, 'm--')
            ax.plot(data.index, t_predictions, 'c--')
            
    plt.setp(plt.gcf().get_axes())
    plt.show()

def plot_all_stocks (prices, returns, method = None, extrema = None):
    i = 0
    while i < len(prices.columns) - 1:
        num = i/9 + 1
        if method == "relative":
            plot_nine_stocks(returns.iloc[:,i:], num, method, extrema)
        else:
            plot_nine_stocks(prices.iloc[:,i:], num, method, extrema)
        i += 9
        
def plot_heatmap (prices):
    cor_matrix = prices.corr()
    sns.heatmap(cor_matrix)
    plt.show()

def information_ratio(returns, benchmark_returns):
    l = min(len(returns), len(benchmark_returns))
    returns = returns[:l]
    benchmark_returns = benchmark_returns[:l]
    return_difference = returns - benchmark_returns
    print(benchmark_returns)
    volatility = return_difference.std() * np.sqrt(l)
    information_ratio = return_difference.mean() / volatility
    return information_ratio
    
def visualize():
    version_msg = "%prog 1.0"
    usage_msg = """%prog FILE [OPTIONS]
Generate plots of stocks. Input a file containing ticker symbols separating by newline character. Must have generated stock price dataframe with same period and interval."""

    parser = OptionParser(version=version_msg,
                          usage=usage_msg)
    parser.add_option("-r", "--residual",
                      action="store_true", dest="residual", default=False,
                      help="plot residuals with respect to SPY")
    parser.add_option("-l", "--relative",
                      action="store_true", dest="relative", default=False,
                      help="plot returns as compared to SPY")
    parser.add_option("-e", "--extrema",
                      action="store", dest="extrema", type = "int", default=None,
                      help="plot local extrema of given window size")
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
        closing_prices = pickle.load(open(file_name + "_closing_price.p", "rb"))
        returns = pickle.load(open(file_name + "_opening_returns.p", "rb"))
    else:
        print("input file missing")
        exit(1)
        
    extrema = None
    if options.extrema:
        if options.extrema <= 0:
            print("Window size cannot be less than or equal to 0")
            exit(1)
        elif options.extrema > len(opening_prices):
            print("Window size cannot be greater than length of price history")
            exit(1)
        else:
            extrema = options.extrema

    if options.residual:
        plot_all_stocks(opening_prices, returns, "residuals", extrema)
    elif options.relative:
        plot_all_stocks(opening_prices, returns, "relative", extrema)
    else:
        plot_all_stocks(opening_prices, returns, "default", extrema)
    

if __name__ == '__main__':
    visualize()
