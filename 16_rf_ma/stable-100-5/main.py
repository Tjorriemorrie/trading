import logging
import os
import pickle
import operator
import gzip
import pandas as pd
import numpy as np


def loadData(currency, interval):
    logging.info('Data: loading {0} at {1}...'.format(currency, interval))
    df = pd.read_csv(
        r'{0}/../../data/{1}e{2}.csv'.format(os.path.realpath(os.path.dirname(__file__)), currency, interval),
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        parse_dates=[[0, 1]],
        index_col=0,
    ).astype(float)
    logging.info('Data: {0} rows loaded'.format(len(df)))
    df = df[-2000:]
    return df


def loadQ(currency, interval):
    logging.info('Q: loading...')
    try:
        filename = '{0}/models/{1}_{2}.pklz'.format(os.path.realpath(os.path.dirname(__file__)), currency, interval)
        with gzip.open(filename) as fz:
            q = pickle.load(fz)
    except (IOError, EOFError) as e:
        logging.error('Could not load Q for {0}'.format(currency))
        q = {}
    logging.info('Q: loaded {0}'.format(len(q)))
    return q


def saveQ(currency, interval, q):
    logging.info('Q: saving...')
    filename_tmp = '{0}/models/tmp.pklz'.format(os.path.realpath(os.path.dirname(__file__)))
    filename = '{0}/models/{1}_{2}.pklz'.format(os.path.realpath(os.path.dirname(__file__)), currency, interval)
    with gzip.open(filename_tmp, 'wb') as fz:
        pickle.dump(q, fz)
        os.rename(filename_tmp, filename)
    logging.info('Q: saved {0}'.format(len(q)))


def getBackgroundKnowledge(df, periods):
    logging.info('Background knowledge: retrieving...')

    # HLC
    hlc = df.apply(lambda x: (x['high'] + x['low'] + x['close']) / 3, axis=1)

    for x in periods:
        avg_x = pd.rolling_mean(hlc, x)
        avg_x_yesterday = avg_x.shift(+1)
        df['ma_{0}_bullish'.format(x)] = avg_x >= avg_x_yesterday
        avg_x_delta = abs(avg_x - avg_x_yesterday)
        avg_x_delta_yesterday = avg_x_delta.shift(+1)
        df['ma_{0}_divergence'.format(x)] = avg_x_delta >= avg_x_delta_yesterday
        df['ma_{0}_magnitude'.format(x)] = avg_x_delta > avg_x_delta.mean()

    for x in periods:
        for y in periods:
            if y <= x:
                continue
            logging.info('MA for {0} and {1}'.format(x, y))
            avg_x = pd.rolling_mean(hlc, x)
            avg_y = pd.rolling_mean(hlc, y)
            df['ma_{0}_crossover_{1}_bullish'.format(x, y)] = avg_x >= avg_y

            ma_diff = avg_x - avg_y
            avg_x_yesterday = avg_x.shift(+1)
            avg_y_yesterday = avg_y.shift(+1)
            ma_diff_yesterday = avg_x_yesterday - avg_y_yesterday
            df['ma_{0}_crossover_{1}_divergence'.format(x, y)] = ma_diff >= ma_diff_yesterday
            df['ma_{0}_crossover_{1}_magnitude'.format(x, y)] = ma_diff >= ma_diff.mean()

    logging.info('Background knowledge: retrieved')
    return df


def summarizeActions(q):
    summary_total = {}
    summary_count = {}
    for key, value in q.iteritems():
        state, action = key.split('|')
        # total
        action_total = summary_total.get(action, 0)
        action_total += value
        action_total /= 2
        summary_total[action] = action_total

        action_count = summary_count.get(action, 0)
        action_count += 1
        summary_count[action] = action_count

    summary_sorted = sorted(summary_total.items(), key=operator.itemgetter(1))

    for action, info in summary_sorted:
        logging.error('{0:10s} after {2} states with {1:.4f} avg'.format(action, info, summary_count[action]))


def calculateActions(min_trail):
    actions = []
    for n in xrange(min_trail, min_trail+100, 5):
        actions.append('buy-{0}'.format(n))
        actions.append('sell-{0}'.format(n))
    return actions
