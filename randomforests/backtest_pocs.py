import pandas as pd
import numpy as np
from features import FeatureFactory
import matplotlib.pyplot as plt
import random as rd
import sklearn as sk
from sklearn.externals import joblib


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

rd.shuffle(currencies)

total = {}
totalTrades = {}
for currency in currencies:

    # load data
    df = pd.read_csv(
        r'../data/' + currency + '1440.csv',
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
    )
    data = df.as_matrix()
    opens = data[:, 2].astype(float)
    highs = data[:, 3].astype(float)
    lows = data[:, 4].astype(float)
    closes = data[:, 5].astype(float)
    volumes = data[:, 6].astype(int)
    print '\n' + currency

    rfc = joblib.load('models/' + currency + '.pkl')

    # calculating features
    ff = FeatureFactory()
    X_scaled = ff.getFeatures(opens, highs, lows, closes, volumes)

    # set rewards
    # print '\ncalculating rewards...'
    rewards = ff.getRewards(closes)  # print rewards

    # train split
    # print '\nsplitting training set'
    X_train, X_test, y_train, y_test = ff.getSplit(X_scaled, rewards)

    # simulate
    fails = []
    his = {}
    zeros = [0] * 11
    ones = [0] * 11
    twos = [0] * 11
    threes = [0] * 11
    fours = [0] * 11
    fives = [0] * 11
    sixes = [0] * 11
    sevens = [0] * 11
    eights = [0] * 11
    nines = [0] * 11
    tens = [0] * 11
    for i, x in enumerate(X_test):
        pos = i + len(X_train)
        item = data[pos]
        # predict
        predict = rfc.predict(x)[0]
        # reward
        reward = rewards[pos]
        # diff
        diff = predict - reward
        # print diff, '<-', predict, 'from', reward
        if diff:
            fails.append({'diff': diff, 'date': item[0] + ' ' + item[1], 'predict': predict, 'reward': reward})

        if diff == 0:


        if diff not in his:
            his[diff] = 0
        his[diff] += 1

    fails.sort(key=lambda x: x['diff'], reverse=True)
    print np.asarray(fails[:4])
    print np.asarray(fails[-4:])
    plt.bar(his.keys(), his.values())
    plt.show()

    plt.bar(range(len(losses)), losses, color='r')
    plt.bar(range(len(wins)), wins, color='g')
    plt.show()

    break

# print '\n\n'
# for cur, profit in total.iteritems():
#     trades = totalTrades[cur]
#     profit = profit if 'JPY' not in cur else profit / 100
#     profitPerTrade = profit / trades
#     print str(cur) + ' ' + str(round(profitPerTrade, 4)) + ' [' + str(profit) + '/' + str(trades) + ']'
