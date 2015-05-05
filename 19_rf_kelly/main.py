import logging as log
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale
from sklearn.cross_validation import train_test_split
from indicators import ewma, rsi


DATA = [
    {'currency': 'AUDUSDe', 'timeframe': 1440},
    {'currency': 'EURGBPe', 'timeframe': 1440},
    {'currency': 'EURJPYe', 'timeframe': 1440},
    {'currency': 'EURUSDe', 'timeframe': 1440},
    {'currency': 'GBPJPYe', 'timeframe': 1440},
    {'currency': 'GBPUSDe', 'timeframe': 1440},
    {'currency': 'NZDUSDe', 'timeframe': 1440},
    {'currency': 'USDCADe', 'timeframe': 1440},
    {'currency': 'USDCHFe', 'timeframe': 1440},
    {'currency': 'USDJPYe', 'timeframe': 1440},
]


def loadData(currency, timeframe):
    log.info('Data: loading...')
    df = pd.read_csv(
        r'../data/{0}{1}.csv'.format(currency, timeframe),
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        parse_dates=[['date', 'time']],
        index_col=0,
    )
    # print df
    log.info('Data: {0} loaded'.format(len(df)))
    return df


def getLabels(df):
    log.info('Getting labels...')
    tmp = df.copy()
    tmp['label'] = tmp['close'].shift(-1)
    tmp['label'] = tmp.apply(lambda x: 'long' if x['label'] - x['close'] >= 0 else 'short', axis=1)
    log.info('Labels set')
    return tmp['label']


def splitAndScale(df, labels):
    log.info('Scaling features')
    features = df.copy()

    # drop
    features.drop(['open', 'high', 'low', 'close', 'volume'], axis=1, inplace=True)

    # split
    X_train, X_test, y_train, y_test = train_test_split(features, labels)

    # scale
    X_train = scale(X_train, axis=0, copy=False)
    X_test = scale(X_test, axis=0, copy=False)

    log.info('Scaled features')
    return X_train, X_test, y_train, y_test


def addEwma(df, fibos):
    log.info('Adding EWMA {0}'.format(fibos))
    ewmas = {}
    for n in fibos:
        ewmas[n] = ewma(df, 'close', n)
    for i, n in enumerate(fibos):
        for m in fibos[i+1:]:
            df['ewma_{0}_{1}'.format(n, m)] = ewmas[n] / ewmas[m]
    log.info('Added EWMA {0}'.format(fibos))


def addRsi(df, fibos):
    log.info('Adding RSI {0}'.format(fibos))
    rsis = {}
    for n in fibos:
        rsis[n] = rsi(df, n)
    for i, n in enumerate(fibos):
        for m in fibos[i+1:]:
            df['rsi_{0}_{1}'.format(n, m)] = rsis[n] / rsis[m]

    df.replace(to_replace=[np.inf, -np.inf], value=0, method='ffil', inplace=True)
    df.fillna(0, inplace=True)

    log.info('Added RSI {0}'.format(fibos))


