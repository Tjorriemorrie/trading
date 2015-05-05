import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.cross_validation import cross_val_score
import sklearn as sk
from features import *
from os.path import isfile, join, realpath
from os import listdir
import json


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

total = {}
totalTrades = {}
totalRatios = {}
for currency in currencies:
    print '\n' + currency

    model = 'models/{0}.pkl'.format(currency.upper())
    rfc = sk.externals.joblib.load(model)

    pathData = realpath('data/{0}'.format(currency.upper()))
    onlyfiles = sorted([f for f in listdir(pathData) if isfile(join(pathData, f))])
    data = {}
    for file in onlyfiles:
        with open(pathData + '/' + file, 'rb') as f:
            fileData = json.loads(f.read())
            data = dict(data.items() + fileData.items())
    print 'data loaded'

    features = extractFeatures(data)
    print len(features), 'features extracted'
    print json.dumps(features[-1], indent=4)

    rewards = calcRewards(data)
    print len(rewards), 'rewards calculated'
    print json.dumps(rewards[-10:-5], indent=4)

    # split sets
    X_train, X_test, y_train, y_test = getSplit(features, rewards)
    print 'sets splitted'

    closes = [v['rate'] for v in data.values()]
    size = len(features)
    cutOff = int(size * 0.70)
    closes = closes[cutOff:]
    print len(closes), 'closes extracted'

    # simulate
    action = 'none'
    trades = 0
    start = 0
    profits = []
    for i, x in enumerate(X_test):
        pos = i  # + len(features)
        print i, action

        # predict
        predict = rfc.predict(x)[0]

        # if new action, take profit/loss
        if predict != action:
            print 'need to go', predict
            closeStart = closes[start]
            closeEnd = closes[pos]
            if action == 'long':
                profit = closeEnd - closeStart
            elif action == 'short':
                profit = closeStart - closeEnd
            else:
                profit = 0
            if profit:
                print i, 'start', closeStart, 'end', closeEnd, 'profit', profit
                trades += 1
            else:
                print 'entering', predict
            start = pos
            action = predict
            profits.append(profit)

    wins = sum([1. for p in profits if p > 0])
    ratio = wins / trades
    total[currency] = sum(profits)
    totalTrades[currency] = trades
    totalRatios[currency] = ratio
    print 'Total = ' + str(sum(profits))
    print 'Trades = ' + str(trades)
    print 'Ratios = ' + str(ratio)

print '\n\n'
for cur, profit in total.iteritems():
    trades = totalTrades[cur]
    profit = profit if 'JPY' not in cur else profit / 100
    profitPerTrade = profit / trades
    print str(cur) + ' ' + str(round(profitPerTrade, 4)) + ' [' + str(profit) + '/' + str(trades) + ']'