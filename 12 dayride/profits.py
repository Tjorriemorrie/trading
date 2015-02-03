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
        print df

        df_monthly = df.groupby(pd.TimeGrouper(freq='M'))
        results = {'max': [], 'close': []}
        for name, group in df_monthly:
            print '\n'
            print 'name'
            print name
            # print 'group'
            # print group

            min_ix = group['low'].idxmin()
            print 'row min index {0}'.format(min_ix)
            max_ix = group['high'].idxmax()
            print 'row max index {0}'.format(max_ix)
            diff_ix = (max_ix - min_ix).days
            print 'date diff {0}'.format(diff_ix)

            row_min = group.loc[group['low'].idxmin()]
            # print 'minrow {0}'.format(minrow)
            row_max = group.loc[group['high'].idxmax()]
            # print 'row max {0}'.format(row_max)
            trade_type = 'buy' if diff_ix else 'sell'
            print 'trade type {0}'.format(trade_type)
            profit_max = row_max['high'] - row_min['low']
            print 'max profit {0}'.format(profit_max)
            profit_close = group['close'].iloc[-1] - group['close'].iloc[0]
            print 'close diff {0}'.format(profit_close)
            profit_perc = abs(profit_close / profit_max)
            print '% {0}'.format(profit_perc)

            # profits.append(profit_perc)
            results['max'].append(profit_max)
            results['close'].append(profit_close)
            # break

        results_df = pd.DataFrame(results)
        print results_df
        results_df.plot()
        plt.show()

        break


def loadData(currency):
    logging.info('Data: loading {0}...'.format(currency))
    df = pd.read_csv(
        r'{0}/../../data/{1}1440.csv'.format(realpath(dirname(__file__)), currency),
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