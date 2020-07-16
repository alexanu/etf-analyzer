#! /usr/bin/python

import pickle
import pandas as pd
import requests, io

def map_stocks():
    r = requests.get("https://www.ishares.com/us/products/239707/ishares-russell-1000-etf/1467271812596.ajax?fileType=csv&fileName=IWB_holdings&dataType=fund")
    df = pd.read_csv(io.BytesIO(r.content), skiprows=9)
    df = df[:1001]
    symbol_lookup = df.set_index('Ticker')[['Name', 'Sector']].T.apply(tuple).to_dict()
    pickle.dump(symbol_lookup, open("russell_1000_symbol_sector_lookup.p", "wb"))
    
if __name__ == '__main__':
    map_stocks()
