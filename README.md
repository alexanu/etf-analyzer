# investing-tool

Files Included:

*generate_stocks.py*: Given a list of ticker symbols, fetches Yahoo
Finance stock data. Returns 3 Pickle objects: opening prices, closing
prices, and opening returns.

*grab_ishares_etf_holdings.py*: given an iShares ETF symbol, fetches
 the iShares holdings csv file from www.ishares.com and generates the
 ticker symbol list, along with the name / sector annotation file.

*cluster_stocks.py*: applys PCA and k-means clustering based on
 intraday price movement to classify a list of stock symbols

*predict.py*: Uses linear regression on local minima and maxima
to predict upper and lower bounds on future stock price. The primary
idea is that, when the stock price nears the projected local maxima,
the likelihood of a correction is high. Note: this model does not
perform in actuality when back-tested on SPY, as it defaults to
assumining that the past trends will continue.

*visualize_stocks.py*; Given a list of ticker symbols, generates
plots of one of the following 3 options: opening stock price, returns
relative to SPY, or residual opening price (after regressing effect of
SPY). If given the --extrema option, also plots regression lines of
the local minima and maxima.

*annotate_reference_stocks.py*: maps the Ruseell 1000 stock symbols
to the company name and sector, for use in future clustering analysis

