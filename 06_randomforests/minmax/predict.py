import logging
import pandas as pd
import numpy as np
from pprint import pprint
from sklearn import cross_validation, externals
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.preprocessing import scale, MinMaxScaler
from progressbar import ProgressBar


currencies = [
    'GBPUSD',
    'AUDUSD',
    'USDCHF',
    'NZDUSD',
    'USDCAD',
    # 'EURGBP',
    # 'EURUSD',

    'USDJPY',
    'EURJPY',
    # 'GBPJPY',
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
        # print data.tail()

        # slice to latest only
        data = data[-50:]

        # extract features
        features = extractFeatures(data)
        # print features.tail()

        # load classifier
        rfc = externals.joblib.load('models/' + currency + '.pkl')
        logging.info('Classifier loaded')

        # predict
        predict_before = rfc.predict(features[-2:-1])[0]
        latest = data[-1:]
        predict = rfc.predict(features[-1:])[0]
        results[currency] = '{0} {1} {2} {3} {4}'.format(
            latest.index[0],
            round(latest['close'], 4),
            predict_before,
            predict,
            '<- changed' if predict != predict_before else '',
        )

    logging.info('Results:')
    for currency, predict in results.iteritems():
        logging.info('{0} {1}'.format(currency, predict))


def extractFeatures(data):
    logging.info('Features: extracting...')
    df = pd.DataFrame(dtype=float, columns=['volume_19', 'volume_18', 'volume_13', 'volume_12', 'volume_11', 'volume_10', 'volume_17', 'volume_16', 'volume_15', 'volume_14', 'low_14', 'low_15', 'low_16', 'low_17', 'low_10', 'low_11', 'low_12', 'low_13', 'low_18', 'low_19', 'close_8', 'close_6', 'close_7', 'close_4', 'close_5', 'close_2', 'close_3', 'high_9', 'high_8', 'high_7', 'high_6', 'high_5', 'high_4', 'high_3', 'high_2', 'high_1', 'close_9', 'open_19', 'open_18', 'open_13', 'open_12', 'open_11', 'open_10', 'open_17', 'open_16', 'open_15', 'open_14', 'close_18', 'close_19', 'close_10', 'close_11', 'close_12', 'close_13', 'close_14', 'close_15', 'close_16', 'close_17', 'volume_9', 'volume_8', 'volume_7', 'volume_6', 'volume_5', 'volume_4', 'volume_3', 'volume_2', 'volume_1', 'close_20', 'open_3', 'open_2', 'open_1', 'open_7', 'open_6', 'open_5', 'open_4', 'high_17', 'high_16', 'high_15', 'open_8', 'high_13', 'high_12', 'high_11', 'high_10', 'high_19', 'high_18', 'open_20', 'open_9', 'high_14', 'low_2', 'low_3', 'low_1', 'low_6', 'low_7', 'low_4', 'low_5', 'low_8', 'low_9', 'close_1', 'volume_20', 'high_20', 'low_20'])
    for i in xrange(20, len(data)+1):
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
    logging.info('Features: extracted')
    return df


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )
    main()