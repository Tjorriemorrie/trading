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
    # 'AUDUSD',
    # 'EURGBP',
    # 'EURJPY',
    # 'EURUSD',
    'GBPJPY',
    # 'GBPUSD',
    # 'NZDUSD',
    # 'USDCAD',
    # 'USDCHF',
    # 'USDJPY',
]


def main(features_num, rewards_num):
    logging.info('Features {0}'.format(features_num))
    logging.info('Rewards {0}'.format(rewards_num))

    for currency in currencies:
        logging.info('Currency: {0}'.format(currency))

        # get data
        data = pd.read_csv(
            r'{0}/../data/{1}1440.csv'.format(realpath(dirname(__file__)), currency),
            names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
            parse_dates=[[0, 1]],
            index_col=0,
        ).astype(float)
        logging.info('Loaded {0} rows'.format(len(data)))
        print data

        # set rewards
        rewards = calculateRewards(data, rewards_num)
        # print rewards

        # extract features
        features = extractFeatures(data, features_num)
        # print features

        features['rewards'] = rewards[-len(features):].values
        features.dropna(inplace=True)
        # print features

        # saving
        features.to_csv('{0}/data/{1}_{2}_{3}.csv'.format(realpath(dirname(__file__)), currency, features_num, rewards_num))


def extractFeatures(data, n):
    logging.info('Features: extracting {0}...'.format(n))

    # create DF
    columns = []
    col_names = ['open', 'high', 'low', 'close', 'volume']
    for col_name in col_names:
        for m in xrange(1, n+1):
            columns.append('{0}_{1}'.format(col_name, m))
    # pprint(columns)
    df = pd.DataFrame(dtype=float, columns=columns)

    pb = ProgressBar(maxval=len(data)).start()
    for i in xrange(n, len(data)+1):
        pb.update(i)
        slice = data.ix[i-n:i]
        # print slice
        scale(slice, axis=0, copy=False)
        # print slice
        cntr = 0
        item = {}
        for slice_index, slice_row in slice.iterrows():
            cntr += 1
            # print slice_index
            # print slice_row
            for col in slice.columns:
                item['{0}_{1}'.format(col, cntr)] = slice_row[col]
        # pprint(item)
        df.loc[i] = item
        # break
    pb.finish()

    logging.info('Features: extracted')
    return df


def calculateRewards(data, n):
    logging.info('Rewards: calculating {0}...'.format(n))

    # get tick changes
    diffs = data['close'].diff(1)
    # print 'DIFFS'
    # print diffs

    # get rolling sum
    sums = pd.rolling_sum(diffs, n)
    # print 'SUMS'
    # print sums

    # shift
    rewards = sums.shift(-n)
    # print 'SHIFTS'
    # print rewards

    # label data
    rewards[rewards >= 0] = 'bull'
    rewards[rewards < 0] = 'bear'
    # print rewards

    logging.info('Rewards: calculated')
    return rewards


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    parser = argparse.ArgumentParser()
    parser.add_argument('features')
    parser.add_argument('rewards')
    args = parser.parse_args()

    main(int(args.features), int(args.rewards))