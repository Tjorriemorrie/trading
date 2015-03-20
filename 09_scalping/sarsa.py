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

CURRENCIES = [
    #'AUDUSD',
    #'EURGBP',
    #'EURJPY',
    'EURUSD',
    #'GBPJPY',
    #'GBPUSD',
    #'NZDUSD',
    #'USDCAD',
    #'USDCHF',
    #'USDJPY',
]

INTERVALS = [
    # '60',
    '1440',
]

ACTIONS = []


def loadData(currency, interval):
    # print 'loading dataframe...'
    df = pd.read_csv(
        r'../data/' + currency.upper() + interval + '.csv',
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        dtype={'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float', 'volume': 'int'},
        #parse_dates=[[0, 1]],
        # index_col=0,
    )
    return df


def loadThetas(currency, interval, cntFeatures):
    # print 'loading thetas'
    try:
        with open('models/{0}_{1}.thts'.format(currency, interval), 'r') as f:
            thetas = pickle.load(f)
    except IOError:
        thetas = np.random.rand(cntFeatures)
    # print 'thetas loaded'
    return thetas


def saveThetas(currency, interval, thetas):
    # print 'saving thetas'
    with open('models/{0}_{1}.thts'.format(currency, interval), 'w') as f:
        pickle.dump(thetas, f)
    # print 'thetas saved'


def createActions(df):
    df['range'] = df['high'] - df['low']
    return list(df['range'].quantile([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]))


def getReward(dfs, a, ACTIONS, RATIOS):
    '''
    always long
    see if target reached
    '''
    ratio = sum(RATIOS) / len(RATIOS)
    print 'ratio', ratio
    profitGoal = ACTIONS[a]
    print 'profit goal', profitGoal
    profitExp = ratio * profitGoal
    print 'profit exp', profitExp
    lossExp = profitExp * -0.95
    print 'loss exp', lossExp
    lossGoal = lossExp / (1. - ratio)
    print 'loss goal', lossGoal
    today = dfs.ix[0]
    print 'close', today['close']
    takeProfit = today['close'] + profitGoal
    print 'takeprofit', takeProfit
    stopLoss = today['close'] + lossGoal
    print 'stoploss', stopLoss

    net = None
    for i, d in dfs.iloc[1:].iterrows():
        if d['low'] < stopLoss and d['high'] > takeProfit:
            print 'both triggered :('
            break
        if d['low'] < stopLoss:
            net = lossGoal
            print 'FAIL'
            break
        elif d['high'] > takeProfit:
            net = profitGoal
            print 'iWIN'
            break
        else:
            print 'no exit'
            pass

    return net


def getActionStateValue(thetas, Fsa, a):
    # pprint(Fsa)
    # pprint(thetas[a])
    Qsa = sum(f * t for f, t in zip(Fsa, thetas[a]))
    return float(Qsa)


def getAction(thetas):
    # exploration
    if random() < EPSILON:
        a = choice(range(len(ACTIONS)))
    # exploitation
    else:
        aMax = None
        QsaHighest = -1000
        for a, aValue in enumerate(ACTIONS):
            #Qsa = getActionStateValue(thetas, features[a], a)
            Qsa = thetas[a]
            if Qsa > QsaHighest:
                QsaHighest = Qsa
                aMax = a
        a = aMax
    return a


ff = FeatureFactory()
ALPHA = 0.1
EPSILON = 0.1
GAMMA = 0.9
if __name__ == '__main__':
    interval = choice(INTERVALS)
    for currency in CURRENCIES:
        print '\n', currency, interval

        # load data
        df = loadData(currency, interval)
        dfIndex = df.index.values
        #print df

        ACTIONS = createActions(df)
        pprint(ACTIONS)

        # create ratios
        RATIOS = [0.50] * 10

        # load thetas
        thetas = loadThetas(currency, interval, len(ACTIONS))
        #pprint(thetas)

        # train
        outcomes = []
        durations = []
        for i in xrange(100):

            # initialize state and action
            a = getAction(thetas)
            #print 'a', a, ACTIONS[a]

            #pprint(dfIndex)
            s = choice(dfIndex)
            #print 's', s
            dfs = df.iloc[s:].reset_index()
            #print dfs.head()

            # set of features at state/index and action/noeffect
            #Fsa = features[s]

            # take action a

            # observe r
            r = getReward(dfs, a, ACTIONS, RATIOS)
            #print 'r', r
            if r is None:
                print 'no reward established'
                continue

            # update ratios
            RATIOS.append(1 if r > 0 else 0)
            while len(RATIOS) > 100:
                RATIOS.pop(0)
            print 'win ratio', int(sum(RATIOS) / len(RATIOS) * 100), r

            # Qsa (action-state-values)
            Qsa = thetas[a]
            #print 'Qsa', Qsa

            ##########################################################################
            # next state
            ss = dfs.ix[1]

            # get next action
            aa = getAction(thetas)
            #print 'aa', aa, ACTIONS[aa]

            # get features and Qsa
            #Fsa = features[aa]
            Qssaa = thetas[aa]

            # delta
            delta = r - Qsa + GAMMA * Qssaa
            #print 'delta', delta

            # update thetas
            thetas[a] = thetas[a] + ALPHA * delta

            # normalize thetas
            minT = min(thetas)
            maxT = max(thetas)
            rangeT = maxT - minT
            # print 'N', 'min', mmin, 'max', mmax, 'range', rrange
            thetas = [(maxT - t) / rangeT for t in thetas]
            # print s, 'normalized', min(thetas[a]), max(thetas[a])

        print 'thetas'
        pprint(zip(ACTIONS, thetas))
        saveThetas(currency, interval, thetas)
