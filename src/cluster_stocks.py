#! /usr/bin/python

from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA 
import pickle
import pandas as pd
import sys
from optparse import OptionParser

def prepare(op, cl):
    movements = (cl - op) / op
    movements = movements.transpose()
    normalizer = Normalizer()
    movements =	normalizer.fit_transform(movements)
    return movements

def k_cluster(movements):
    numStocks = len(movements)
    if numStocks < 50:
        clusters = 5
    else:
        clusters = min(10, 5 + (numStocks - 50) / 10 )
    
    kmeans = KMeans(n_clusters=clusters, max_iter=1000)
    kmeans.fit(movements)
    labels = kmeans.predict(movements)
    return labels
    
def pca_cluster(movements):
    reduced_data = PCA(n_components = 2).fit_transform(movements)
    return k_cluster(reduced_data)
    
if __name__ == '__main__':

    version_msg = "%prog 1.0"
    usage_msg = """%prog FILE [OPTIONS] 
    Performs clustering on stocks based on daily movements (closing price - opening price)."""
    parser = OptionParser(version=version_msg,
                          usage=usage_msg)
    parser.add_option("-p", "--period",
                      action="store", dest="period", type = "string", default=None,
                      help="valid periods are 1mo, 3mo, 6mo, 1y, 2y, 5y")
    parser.add_option("-i", "--interval",
                      action="store", dest="interval", type = "string", default=None,
                      help="valid periods are 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
    parser.add_option("-r", "--reduction",
                      action="store_true", dest="pca", default=False,
                      help="perform principal component analysis prior to k-means")
    parser.add_option("-m", "--mapper",
                      action="store", dest="mapper", type = "string", default=None,
                      help="if symbol_sector_lookup.p dictionary was generated, enter the name of the file here \
                           if nothing is entered, output file will not have sector and company names annotated")
    
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

    if len(opening_prices.columns) < 20:
        print("Input file must have at least 20 stocks for clustering")
        exit(1)
        

    
    movements = prepare(opening_prices, closing_prices)

    perform_pca = options.pca
    if perform_pca:
        labels = pca_cluster(movements)
    else:
        labels = k_cluster(movements)

    mapper = options.mapper
    df = pd.DataFrame(data={'Label': labels, 'Symbol': opening_prices.columns})
    if mapper:
        ref = pickle.load(open(mapper, "rb"))
        annotations = df['Symbol'].map(ref)
        tmp = pd.DataFrame(annotations.tolist())
        tmp.columns = ['Name', 'Sector', 'Market Cap']
        df = df.merge(tmp, left_index=True, right_index=True)
        df['Market Cap'] = df['Market Cap'].str.replace(',','')
        df['Market Cap'] = df['Market Cap'].astype('float64')
        df = df.sort_values(by=['Label', 'Market Cap'], ascending=(True, False))

    if perform_pca:
        df.to_csv(file_name + "_pca_k_clustered.csv", index = False)
    else:
        df.to_csv(file_name + "_k_clustered.csv", index = False)
    
