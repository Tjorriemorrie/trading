import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.cross_validation import cross_val_score
from features import FeatureFactory
import sklearn as sk

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

    rfc = sk.externals.joblib.load('models/' + currency + '.pkl')

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
    action = 'none'
    trades = 0
    start = 0
    profits = []
    for i, x in enumerate(X_test):
        pos = i + len(X_train)
        # predict
        predict = rfc.predict(x)[0]

        if predict != action:
            if action != 'none':
                closeStart = closes[start]
                closeEnd = closes[pos]
                if action == 'long':
                    profit = closeEnd - closeStart
                else:
                    profit = closeStart - closeEnd
                profits.append(profit)
                trades += 1
                print data[start][0] + ' till ' + data[pos][0] + ' on ' + str(action) + ' = ' + str(profit)
            start = pos
            action = predict

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
    ratio = int(totalRatios[cur] * 100)
    profit = profit if 'JPY' not in cur else profit / 100
    profitPerTrade = profit / trades
    print cur, ratio, round(profitPerTrade, 4), '[', profit, '/', trades, ']'
