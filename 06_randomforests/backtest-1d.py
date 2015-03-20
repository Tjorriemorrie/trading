import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.cross_validation import cross_val_score
from features import FeatureFactory
import sklearn as sk
from pprint import pprint

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
for currency in currencies:
    print '\n' + currency

    # load data
    df = pd.read_csv(
        r'../data/' + currency + '1440.csv',
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
    )
    data = df.as_matrix()

    # train on first 60%
    data = data[-int(len(data) * 0.40):]

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
    rewards = ff.getRewards(closes)

    # simulate
    action = 'none'
    trades = []
    for i, x in enumerate(X_scaled):
        pos = i

        # actual (what happened tomorrow)
        reward = rewards[pos]

        # predict
        predict = rfc.predict(x)[0]

        goal = True if predict == reward else False
        print data[pos][0], 'p:', predict, 'a:', reward

        trades.append(goal)

    wins = sum([1. for t in trades if t])
    ratio = wins / len(trades)
    total[currency] = ratio
    print 'Ratio', ratio

print '\n\n'
for cur, ratio in total.iteritems():
    print cur, int(ratio * 100)
