'''
looping, infinite & random
'''

import pandas as pd
import numpy as np
from features import FeatureFactory
import pickle
from random import random, choice
from pprint import pprint
import time

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

intervals = [
    # '60',
    '1440',
]

actions = [
    'stay-out',
    'enter-long',
    'stay-long',
    'exit-long',
    'enter-short',
    'stay-short',
    'exit-short',
]

def loadData(currency, interval):
    # print 'loading dataframe...'
    df = pd.read_csv(
        r'../data/' + currency.upper() + interval + '.csv',
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        dtype={'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float', 'volume': 'int'},
        # parse_dates=[[0, 1]],
        # index_col=0,
    )
    # print df.tail()

    data = df.as_matrix()
    opens = data[:, 2].astype(float)
    highs = data[:, 3].astype(float)
    lows = data[:, 4].astype(float)
    closes = data[:, 5].astype(float)
    volumes = data[:, 6].astype(int)
    # print 'dataframe loaded'

    return opens, highs, lows, closes, volumes


def loadThetas(currency, interval, cntFeatures):
    # print 'loading thetas'
    try:
        with open('models/{0}_{1}.thts'.format(currency, interval), 'rb') as f:
            thetas = pickle.load(f)
    except IOError:
        thetas = [np.random.rand(cntFeatures) for a in actions]
    # pprint(thetas)
    # print 'thetas loaded'
    return thetas


def saveThetas(currency, interval, thetas):
    # print 'saving thetas'
    with open('models/{0}_{1}.thts'.format(currency, interval), 'wb') as f:
        pickle.dump(thetas, f)
    # print 'thetas saved'


def getActionStateValue(thetas, Fsa, a):
    # pprint(Fsa)
    # pprint(thetas[a])
    Qsa = sum(f * t for f, t in zip(Fsa, thetas[a]))
    return float(Qsa)


def getActionsAvailable(a):
    # stay-out: stay-out & enter-long & enter-short
    if a == 0:
        return [0, 1, 4]
    elif a == 1:
        return [2]
    elif a == 2:
        return [2, 3]
    elif a == 4:
        return [5]
    elif a == 5:
        return [5, 6]
    else:
        raise Exception('no available actions for {0}'.format(a))


def getAction(thetas, features, a):
    # exploration
    actionsAvailable = getActionsAvailable(a)
    aMax = None
    QsaHighest = -1000
    for a in actionsAvailable:
        Qsa = getActionStateValue(thetas, features[a], a)
        if Qsa > QsaHighest:
            QsaHighest = Qsa
            aMax = a
    a = aMax
    return a


def getActionStateValue(thetas, Fsa, a):
    # pprint(Fsa)
    # pprint(thetas[a])
    Qsa = sum(f * t for f, t in zip(Fsa, thetas[a]))
    return float(Qsa)


ff = FeatureFactory()
alpha = 0.1
epsilon = 0.1
gamma = 0.9
if __name__ == '__main__':
    interval = choice(intervals)
    for currency in currencies:
        # load data
        opens, highs, lows, closes, volumes = loadData(currency, interval)
        dataSize = len(closes)

        # extract features
        features = ff.getFeatures(opens, highs, lows, closes, volumes)
        # pprint(features)

        # load thetas
        thetas = loadThetas(currency, interval, len(features))

        # repeat to get trade
        a = 0
        start = len(features) - 500
        for i in xrange(start, len(features)):
            aa = getAction(thetas, features, a)
            a = aa

        # display last action
        print currency, actions[a]