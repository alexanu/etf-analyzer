#! /usr/local/bin/python3

import simfin as sf
import seaborn as sns
import pandas as pd
import pickle
import sys
from optparse import OptionParser

"""
Simfin module tutorial here: https://github.com/SimFin/simfin-tutorials/blob/master/09_Machine_Learning.ipynb
"""

if __name__ == '__main__':

    version_msg = "%prog 1.0"
    usage_msg = """%prog FILE [OPTIONS]
    Get financial data from SimFin for fundamental analysis."""

    parser = OptionParser(version=version_msg,
                          usage=usage_msg)
    parser.add_option("-r", "--recent",
                      action="store_true", dest="recent", default=True,
                      help="only look at most recent values")
    parser.add_option("-c", "--clean",
                      action="store_true", dest="clean", default=False,
                      help="only keep rows with no NA values")

    options, args = parser.parse_args(sys.argv[1:])


    recent = options.recent


    sf.set_data_dir('./simfin_data/')
    sf.load_api_key(path='./simfin_api_key.txt', default_key='free')
    sns.set_style("whitegrid")

    market = 'us'

    offset = pd.DateOffset(days=60)
    refresh_days = 30
    refresh_days_shareprices = 10

    hub = sf.StockHub(market=market, offset=offset,
                      refresh_days=refresh_days,
                      refresh_days_shareprices=refresh_days_shareprices)
    df_fin_signals = hub.fin_signals(variant='daily')
    df_growth_signals = hub.growth_signals(variant='daily')
    df_val_signals = hub.val_signals(variant='daily')

    dfs = [df_fin_signals, df_growth_signals, df_val_signals]
    df_signals = pd.concat(dfs, axis=1)

    thresh = 0.75 * len(df_signals.dropna(how='all'))
    df_signals = df_signals.dropna(axis='columns', thresh=thresh)

    df_signals = df_signals.unstack()

    pickle.dump(df_signals, open("financial_signals_simfin.p", "wb"))

    if recent:
        last_date = df_signals['P/Sales'].columns[-1]
        mask = df_signals.columns.get_level_values(1) == last_date
        subset = df_signals.columns[mask]
        df_signals = df_signals[subset]
        pickle.dump(df_signals, open("financial_signals_simfin_only_recent.p", "wb"))
    if options.clean:
        final = df_signals.dropna()
        pickle.dump(final, open("financial_signals_simfin_only_recent.p", "wb"))

