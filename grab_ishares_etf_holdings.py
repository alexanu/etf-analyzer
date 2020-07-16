#! /usr/bin/python

import pickle
import re
import pandas as pd
import requests, io, sys
from optparse import OptionParser


"""
Russell 1000: https://www.ishares.com/us/products/239707/ishares-russell-1000-etf/1467271812596.ajax?fileType=csv&fileName=IWB_holdings&dataType=fund
IBB: https://www.ishares.com/us/products/239699/ishares-nasdaq-biotechnology-etf/1467271812596.ajax?fileType=csv&fileName=IBB_holdings&dataType=fund
"""

def map_stocks(link):
    etf_name = re.search("ishares-(.+)-etf",link)
    if etf_name is None:
        print("not a valid ishares etf holdings link")
        exit(1)
    etf_name = etf_name.group(1)

    r = requests.get(link)
    if r.status_code != 200:
        print("Error making request")
        exit(1)
    df = pd.read_csv(io.BytesIO(r.content), skiprows=9)
    df = df[:len(df)-1]
    symbol_lookup = df.set_index('Ticker')[['Name', 'Sector', 'Market Value']].T.apply(tuple).to_dict()
    # tckrs = symbol_lookup.keys()
    tckrs = df['Ticker']
    with open(etf_name + "_ticker_symbols.txt", "w") as outfile1:
        outfile1.write("\n".join(tckrs))
    out_file2 = etf_name + "_symbol_sector_lookup.p"
    pickle.dump(symbol_lookup, open(out_file2, "wb"))

if __name__ == '__main__':
    version_msg = "%prog 1.0"
    usage_msg = """%prog [OPTIONS]
    Creates dictionary mapping ticker symbol to tuple consisting of company name and sector. Input a link to the holdings csv for an iShares etf."""
    parser = OptionParser(version=version_msg,
                          usage=usage_msg)
    parser.add_option("-l", "--link",
                      action="store", dest="link", type="string", default=None,
                      help="link to iShares holdings csv, surrounded by single quotes")
    options, args = parser.parse_args(sys.argv[1:])

    link = options.link
    if link is None:
        print("No iShares holdings link entered")
        exit(1)
    else:
        map_stocks(link)