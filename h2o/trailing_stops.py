import logging
import argparse
from os.path import realpath, dirname
import pandas as pd
import numpy as np
from pprint import pprint
from sklearn import cross_validation, externals
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.preprocessing import scale, MinMaxScaler
from progressbar import ProgressBar


currencies = [
    'AUDUSD',
    'EURGBP',
    'EURJPY',
    'EURUSD',
    'GBPJPY',
    'GBPUSD',
    'NZDUSD',
    'USDCAD',
    'USDCHF',
    'USDJPY',
]


def main():
    for currency in currencies:
        # logging.info('Currency: {0}'.format(currency))

        # get data
        data = pd.read_csv(
            r'{0}/../data/{1}1440.csv'.format(realpath(dirname(__file__)), currency),
            names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
            parse_dates=[[0, 1]],
            index_col=0,
        ).astype(float)[-500:]
        # logging.info('Loaded {0} rows'.format(len(data)))
        # print data

        # get range
        data['rolhigh'] = pd.rolling_max(data['high'], 5)
        data['rolmin'] = pd.rolling_min(data['low'], 5)
        data['range'] = data['rolhigh'] - data['rolmin']
        data.dropna(inplace=True)
        # print data

        # get stats
        mean = data.range.mean()
        std = data.range.std()

        # drop outliers
        min_cutoff = mean - std * 2
        max_cutoff = mean + std * 2
        # logging.info('Dropping outliers between below {0:4f} and above {1:4f}'.format(min_cutoff, max_cutoff))
        data = data[data['range'] > min_cutoff]
        data = data[data['range'] < max_cutoff]
        # logging.info('Dropped {0} rows'.format(500 - len(data)))

        # get stats
        mean = data.range.mean()
        std = data.range.std()
        logging.info('{0} between {1} and {2} [{3}]'.format(
            currency,
            round(mean - std, 4),
            round(mean + std, 4),
            round(mean, 4),
        ))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main()