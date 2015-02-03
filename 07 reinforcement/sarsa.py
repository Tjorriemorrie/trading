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

    return opens[-400:], highs[-400:], lows[-400:], closes[-400:], volumes[-400:]


def loadThetas(currency, interval, cntFeatures):
    # print 'loading thetas'
    try:
        with open('models/{0}_{1}.thts'.format(currency, interval), 'r') as f:
            thetas = pickle.load(f)
    except IOError:
        thetas = [np.random.rand(cntFeatures) for a in actions]
    # pprint(thetas)
    # print 'thetas loaded'
    return thetas


def saveThetas(currency, interval, thetas):
    # print 'saving thetas'
    with open('models/{0}_{1}.thts'.format(currency, interval), 'w') as f:
        pickle.dump(thetas, f)
    # print 'thetas saved'


def getReward(rewards, s, a):
    '''
    if action is stay-out: obviously no reward: we will then only enter trades if we expect positive returns
    if action is exiting: no reward as well: we will not enforce exiting positions, we will only exit when we expect negative returns.
    we get rewards only for entering and keeping positions (as long as positive returns are expected)
    '''
    if a == 0:
        r = 0
    elif a in [3, 6]:
        r = 0
    else:
        r = rewards[s]
    return r


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
    # print 'actions available', actionsAvailable
    if random() < epsilon:
        a = choice(actionsAvailable)
    # exploitation
    else:
        aMax = None
        QsaHighest = -1000
        for a in actionsAvailable:
            Qsa = getActionStateValue(thetas, features[a], a)
            if Qsa > QsaHighest:
                QsaHighest = Qsa
                aMax = a
        a = aMax
    return a


ff = FeatureFactory()
alpha = 0.1
epsilon = 0.1
gamma = 0.9
if __name__ == '__main__':
    interval = choice(intervals)
    for currency in currencies:
        print '\n', currency, interval

        # load data
        opens, highs, lows, closes, volumes = loadData(currency, interval)
        print 'data loaded'
        dataSize = len(closes)

        # extract features
        features = ff.getFeatures(opens, highs, lows, closes, volumes)
        print 'get features'
        cntFeatures = len(features)
        # pprint(features)

        # get rewards
        print 'get rewards'
        rewards = ff.getRewardsCycle(closes)

        # load thetas
        print 'load thetas'
        thetas = loadThetas(currency, interval, cntFeatures)

        # train
        outcomes = []
        durations = []
        print 'start'
        for i in xrange(100):

            # initialize state and action
            a = actions.index('stay-out')
            # print 'a start', a, actions[a]
            # print 'len closes', len(closes)
            # pprint(range(len(closes)))
            s = choice(range(len(closes)))
            # print 's start', s
            iniS = s

            # keep going until we hit an exit (that will be 1 episode/trade)
            while a not in [3, 6]:
                # set of features at state/index and action/noeffect
                Fsa = features[s]

                # take action a

                # observe r
                r = getReward(rewards, s, a)
                # print s, 'r of', r, 'for', actions[a], 'from', iniS, 'till', s

                # next state
                ss = s + 1
                if ss >= dataSize:
                    break

                # Qsa (action-state-values)
                Qsa = getActionStateValue(thetas, Fsa, a)
                # print s, 'Qsa', Qsa

                # start delta
                delta = r - Qsa
                # print s, 'delta start', delta

                # get next action
                aa = getAction(thetas, features, a)
                # print s, 'a', aa, actions[aa]

                # get features and Qsa
                Fsa = features[aa]
                Qsa = getActionStateValue(thetas, Fsa, aa)

                # end delta
                delta += gamma * Qsa
                # print s, 'delta end', delta

                # update thetas
                thetas[a] = [theta + alpha * delta for theta in thetas[a]]
                # pprint(thetas[a])
                # normalize thetas
                # pprint(thetas[a])
                mmin = min(thetas[a])
                mmax = max(thetas[a])
                rrange = mmax - mmin
                # print 'N', 'min', mmin, 'max', mmax, 'range', rrange
                thetas[a] = [(mmax - t) / rrange for t in thetas[a]]
                # print s, 'normalized', min(thetas[a]), max(thetas[a])

                # until s is terminal
                if aa in [3, 6]:
                    outcomes.append(closes[s] - closes[iniS] if aa == 3 else closes[iniS] - closes[s])
                    durations.append(s - iniS)
                    print '\n', '#', len(outcomes), actions[a], r
                    print 'Net outcomes', sum(outcomes)
                    print 'Avg durations', int(sum(durations) / len(durations))
                    wins = sum([1. for o in outcomes if o > 0])
                    print currency, 'Win ratio', int(wins / len(outcomes) * 100)
                    # time.sleep(0.3)

                # if iniS not set, then set it
                if a == 0 and aa in [1, 4]:
                    iniS = s

                # s <- s'  a <- a'
                s = ss
                a = aa

            # save periodically
            if i % 100 == 99:
                saveThetas(currency, interval, thetas)
                # print 'Net outcomes', sum(outcomes)
                # print currency, 'Win ratio', int(wins / len(outcomes) * 100)

        saveThetas(currency, interval, thetas)
