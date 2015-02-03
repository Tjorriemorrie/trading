import pandas as pd
import numpy as np
import sklearn as sk
from features import FeatureFactory
from random import choice, random
import time


ff = FeatureFactory()

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

actions = ['short', 'long']

def getReward(closes, start, end, action):
    closeStart = closes[start]
    closeEnd = closes[end]
    if action == 'short':
        reward = closeStart - closeEnd
    elif action == 'long':
        reward = closeEnd - closeStart
    else:
        raise Exception('unknown action')
    return reward


def sumFeatureWeights(Fsa, weights, action):
    """ Get q value
        Sum feature weights """
    # validate weights
    while len(weights) < len(actions):
        w = []
        for i in range(len(Fsa)):
            w.append(random())
            # w.append(0)
        weights.append(w)

    actionIndex = actions.index(action)
    Qa = [w * f for w, f in zip(weights[actionIndex], Fsa)]
    # print 'Qa = '
    # print Qa
    Qa = sum(Qa)
    # print 'sumFW = ' + str(Qa)
    return Qa


def getAction(Fsa, weights):
    Qsas = []
    for action in actions:
        Qsa = sumFeatureWeights(Fsa, weights, action)
        Qsas.append(Qsa)
    QsaMax = max(Qsas)

    if QsaMax <= 0:
        print str(QsaMax)
        return 'none'
    
    action = actions[Qsas.index(QsaMax)]
    return action


net = {}

for currency in currencies:
    net[currency] = 0
    print '\n\n'
    print currency

    df = pd.read_csv(
        r'../' + currency + '1440.csv',
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
    )

    data = df.as_matrix()
    opens = data[:, 2].astype(float)
    highs = data[:, 3].astype(float)
    lows = data[:, 4].astype(float)
    closes = data[:, 5].astype(float)
    volumes = data[:, 6].astype(int)

    weights = sk.externals.joblib.load('models/' + currency + '.wghts')

    X = ff.getFeatures(opens, highs, lows, closes, volumes)
    X_scaled = sk.preprocessing.scale(X)
    # print len(X_scaled)

    profits = []
    dateStart = data[0][0]
    closeStart = closes[0]
    a = 'long'
    for i in xrange(len(closes)):
        close = closes[i]
        Fsa = X_scaled[i]
        date = data[i][0]
        
        aa = getAction(Fsa, weights)

        # exit/flip trade on new action
        if aa != a:
            if a != 'none':
                # get reward
                if a == 'long':
                    r = close - closeStart
                elif a == 'short':
                    r = closeStart - close
                profits.append(r)
                # print progress
                print dateStart + ' till ' + date + ' on ' + str(a) + ' = ' + str(r)

            # next trade opened (flipped)
            closeStart = close
            dateStart = date

        a = aa

    net[currency] = profits
    
print '\n\n'
for currency, profits in net.iteritems():
    trades = len(profits)
    total = sum(profits)
    total = total if 'JPY' not in currency else total / 100
    profitPerTrade = total / trades
    print str(currency) + ' ' + str(round(profitPerTrade, 4)) + ' [' + str(total) + '/' + str(trades) + ']'
