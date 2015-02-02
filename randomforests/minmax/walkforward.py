import logging
import pandas as pd
import numpy as np
from pprint import pprint
from sklearn import cross_validation, externals
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.preprocessing import scale, MinMaxScaler
from progressbar import ProgressBar


'''
2015-01-28 14:44:00,290 root     INFO     GBPUSD profit 0.0062 [1.7468 0.81]
2015-01-28 14:44:00,308 root     INFO     AUDUSD profit 0.0033 [0.2840 0.65]
2015-01-28 14:44:00,290 root     INFO     USDCHF profit 0.0020 [0.1704 0.58]
2015-01-28 14:44:00,308 root     INFO     NZDUSD profit 0.0020 [0.2946 0.57]
2015-01-28 14:44:00,308 root     INFO     USDCAD profit 0.0001 [0.0117 0.55]

2015-01-28 14:44:00,291 root     INFO     EURGBP profit -0.0012 [-0.1692 0.45]
2015-01-28 14:44:00,308 root     INFO     EURUSD profit -0.0015 [-0.1473 0.43]

2015-01-28 14:44:00,308 root     INFO     USDJPY profit 0.0514 [13.1090 0.51]
2015-01-28 14:44:00,289 root     INFO     EURJPY profit 0.0040 [3.0930 0.49]

2015-01-28 14:44:00,308 root     INFO     GBPJPY profit -0.0154 [-4.5010 0.48]

'''


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
    results = {}
    for currency in currencies:
        logging.info('Currency: {0}'.format(currency))

        # get data
        data = pd.read_csv(
            r'../../data/' + currency + '1440.csv',
            names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
            parse_dates=[[0, 1]],
            index_col=0,
        ).astype(float)
        logging.info('Loaded {0} rows'.format(len(data)))
        # print data

        samples = []
        for sample in np.array_split(data, 10):
            logging.info('')
            logging.info('This sample:')
            # print sample
            sample_res = sample.copy()

            # extract features
            features = extractFeatures(sample)
            # print features.tail()

            # set rewards
            rewards = calculateRewards(sample)
            rewards = rewards[-len(features):]
            # print rewards.tail()

            # train split
            logging.info('Data splitting...')
            cutoff = int(len(sample) * 0.70)
            X_train = features[:cutoff]
            logging.info('X_train set size: {0}'.format(len(X_train)))
            X_test = features[cutoff:]
            logging.info('X_test set size: {0}'.format(len(X_test)))
            y_train = rewards[:cutoff]
            # logging.info('Train set size: {0}'.format(len(X_train)))
            y_test = rewards[cutoff:]

            # create classifier
            logging.info('Classifier: training...')
            # rfc = RandomForestClassifier(n_estimators=30)
            rfc = ExtraTreesClassifier(n_estimators=20, oob_score=True, bootstrap=True)
            rfc.fit(X_train, y_train)

            sample_test = sample_res[-len(X_test):]
            logging.info('Test set size: {0}'.format(len(sample_test)))
            sample_test['predict'] = rfc.predict(X_test)
            # print sample_test.tail()
    
            profits = []
            state = None
            for index, row in sample_test.iterrows():
                # print '{0}'.format(index)
    
                # in trade?
                if state:
                    # exit trade?
                    if state != row['predict']:
                        close_exit = row['close']
                        profit = close_exit - close_entry if state == 'bull' else close_entry - close_exit
                        logging.info('exited {0} at {1} for {2}'.format(state, close_exit, profit))
                        profits.append(profit)
                        state = None
    
                    # remained in trade
                    else:
                        close_exit = row['close']
                        net = close_exit - close_entry if state == 'bull' else close_entry - close_exit
                        logging.info('net {0} at {1} for {2}'.format(state, close_exit, net))
    
                # enter trade?
                if not state:
                    close_entry = row['close']
                    state = row['predict']
                    logging.info('')
                    logging.info('entering {0} at {1}'.format(state, close_entry))

            if not len(profits):
                profits.append(0)
            wins = sum([1. if p > 0. else 0. for p in profits])
            win_ratio = wins / len(profits)
            samples.append({
                'sum': sum(profits),
                'win_ratio': win_ratio,
                'ppt': sum(profits) / len(profits),
            })
            # break

        results[currency] = samples
        # break

    for currency, samples in results.iteritems():
        logging.info('')
        for result in samples:
            logging.info('{0} profit {3:.4f} [{1:.4f} {2:.2f}]'.format(currency, result['sum'], result['win_ratio'], result['ppt']))


def extractFeatures(data):
    logging.info('Features: extracting...')
    df = pd.DataFrame(dtype=float, columns=['volume_19', 'volume_18', 'volume_13', 'volume_12', 'volume_11', 'volume_10', 'volume_17', 'volume_16', 'volume_15', 'volume_14', 'low_14', 'low_15', 'low_16', 'low_17', 'low_10', 'low_11', 'low_12', 'low_13', 'low_18', 'low_19', 'close_8', 'close_6', 'close_7', 'close_4', 'close_5', 'close_2', 'close_3', 'high_9', 'high_8', 'high_7', 'high_6', 'high_5', 'high_4', 'high_3', 'high_2', 'high_1', 'close_9', 'open_19', 'open_18', 'open_13', 'open_12', 'open_11', 'open_10', 'open_17', 'open_16', 'open_15', 'open_14', 'close_18', 'close_19', 'close_10', 'close_11', 'close_12', 'close_13', 'close_14', 'close_15', 'close_16', 'close_17', 'volume_9', 'volume_8', 'volume_7', 'volume_6', 'volume_5', 'volume_4', 'volume_3', 'volume_2', 'volume_1', 'close_20', 'open_3', 'open_2', 'open_1', 'open_7', 'open_6', 'open_5', 'open_4', 'high_17', 'high_16', 'high_15', 'open_8', 'high_13', 'high_12', 'high_11', 'high_10', 'high_19', 'high_18', 'open_20', 'open_9', 'high_14', 'low_2', 'low_3', 'low_1', 'low_6', 'low_7', 'low_4', 'low_5', 'low_8', 'low_9', 'close_1', 'volume_20', 'high_20', 'low_20'])
    pb = ProgressBar(maxval=len(data)).start()
    for i in xrange(20, len(data)+1):
        pb.update(i)
        slice = data.ix[i-20:i]
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
    pb.finish()
    logging.info('Features: extracted')
    return df


def calculateRewards(data):
    logging.info('Rewards: calculating...')
    rewards = data['close'].diff(-1)
    rewards.fillna(0, inplace=True)
    # print rewards.tail()
    rewards[rewards >= 0] = 'bear'
    rewards[rewards < 0] = 'bull'
    # print rewards.tail()
    logging.info('Rewards: calculated')
    return rewards


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )
    main()