import logging
from pprint import pprint
from os.path import realpath, dirname
import pandas as pd
from sklearn.preprocessing import scale
import matplotlib.pyplot as plt


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
    lines = [1, 2, 3, 5, 8, 13, 21]
    results = {}
    for currency in currencies:
        logging.info('Currency: {0}'.format(currency))
        results[currency] = {}

        df = loadData(currency)
        # print df

        df = dropOutliers(df)
        # print df

        df = resistanceLines(df, lines)
        # print df.tail()

        for val in lines:
            high_val = 'high_{0}'.format(val)
            low_val = 'low_{0}'.format(val)
            xo_high_val = 'xo_high_{0}'.format(val)
            xo_low_val = 'xo_low_{0}'.format(val)
            df[xo_high_val] = df['high'] > df[high_val]
            df[xo_low_val] = df['low'] < df[low_val]
            results[currency][high_val] = df[xo_high_val].value_counts()[True] / float(len(df))
            results[currency][low_val] = df[xo_low_val].value_counts()[True] / float(len(df))

        print df[::len(df)/20]
        break

    for currency, data in results.iteritems():
        for line, cnt in data.iteritems():
            logging.info('{0} {1} {2:.2f}'.format(currency, line, cnt))


def loadData(currency):
    logging.info('Data: loading {0}...'.format(currency))
    df = pd.read_csv(
        r'{0}/../data/{1}1440.csv'.format(realpath(dirname(__file__)), currency),
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        parse_dates=[[0, 1]],
        index_col=0,
    ).astype(float)
    logging.info('Data: {0} rows loaded'.format(len(df)))
    return df


def dropOutliers(df):
    logging.info('Dropping outliers...')
    size_start = len(df)

    # get range
    rolhigh = pd.rolling_max(df['high'], 5)
    rolmin = pd.rolling_min(df['low'], 5)
    df['range'] = rolhigh - rolmin
    df.dropna(inplace=True)
    # print df

    # get stats
    mean = df.range.mean()
    std = df.range.std()

    # drop outliers
    min_cutoff = mean - std * 2
    max_cutoff = mean + std * 2
    # logging.info('Dropping outliers between below {0:4f} and above {1:4f}'.format(min_cutoff, max_cutoff))
    df = df[df['range'] > min_cutoff]
    df = df[df['range'] < max_cutoff]
    # logging.info('Dropped {0} rows'.format(500 - len(df)))

    # get stats
    # mean = df.range.mean()
    # std = df.range.std()
    # logging.info('{0} between {1} and {2} [{3}]'.format(
    #     currency,
    #     round(mean - std, 4),
    #     round(mean + std, 4),
    #     round(mean, 4),
    # ))

    logging.info('Outliers: {0} removed'.format(size_start - len(df)))
    return df


def resistanceLines(df, vals):
    logging.info('Resistance lines...')

    # print df.tail()
    for val in vals:
        df['high_{0}'.format(val)] = pd.rolling_max(df['high'], val).shift(1)
        df['low_{0}'.format(val)] = pd.rolling_min(df['low'], val).shift(1)
    # print df.tail()

    df.dropna(inplace=True)

    logging.info('Resistance lines')
    return df
    
    

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main()