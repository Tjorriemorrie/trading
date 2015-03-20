import logging
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

    for currency in currencies:
        logging.info('Currency: {0}'.format(currency))

        df = loadData(currency)
        # print df

        df = dropOutliers(df)
        # print df

        rl = pd.DataFrame(dtype=float)
        rl['high8'] = pd.rolling_max(df['high'], 8)
        rl['high13'] = pd.rolling_max(df['high'], 13)
        rl['high21'] = pd.rolling_max(df['high'], 21)
        rl['high5'] = pd.rolling_max(df['high'], 34)
        rl['low8'] = pd.rolling_min(df['low'], 8)
        rl['low13'] = pd.rolling_min(df['low'], 13)
        rl['low21'] = pd.rolling_min(df['low'], 21)
        rl['low5'] = pd.rolling_min(df['low'], 34)
        print rl.tail(20)

        rl = rl.iloc[-88:-22]
        logging.info('rl length {0}'.format(len(rl)))

        rl.plot()
        # plt.show()
        plt.savefig('resistance_lines.png')

        break


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


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main()