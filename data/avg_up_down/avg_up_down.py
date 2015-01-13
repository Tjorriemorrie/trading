import logging
import pandas as pd
import numpy as np
from pprint import pprint


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
    for currency in currencies[:1]:
        logging.info('Currency: {0}'.format(currency))

        # get data
        data = pd.read_csv(
            r'../' + currency + '1440.csv',
            names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
            parse_dates=[[0, 1]],
            index_col=0,
        ).astype(float)
        logging.info('Loaded {0} rows'.format(len(data)))
        # print data.tail()

        data['avg20'] = pd.rolling_mean(data['close'], 20)
        # print data.head(24)

        data['up_down'] = data['close'] - data['avg20']
        print data.tail()

        grp = data.groupby(pd.TimeGrouper(freq='M')).sum()
        print grp.tail()
        grp['bull_bear'] = grp['up_down'] >= 0
        print grp

        grp['bull_bear'].to_csv('bull_bear_monthly.csv')




if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )
    main()