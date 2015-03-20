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


for currency in currencies:
    print '\n' + currency

    print 'loading...'
    df = pd.read_csv(
        r'../data/' + currency + '1440.csv',
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
    )
    data = df.as_matrix()

    # train on first 60%
    data = data[:int(len(data) * 0.60)]

    opens = data[:, 2].astype(float)
    highs = data[:, 3].astype(float)
    lows = data[:, 4].astype(float)
    closes = data[:, 5].astype(float)
    volumes = data[:, 6].astype(int)

    # calculating features
    print 'calculating features...'
    ff = FeatureFactory()
    X_scaled = ff.getFeatures(opens, highs, lows, closes, volumes)
    # print X_scaled

    # set rewards
    print 'calculating rewards...'
    rewards = ff.getRewards(closes)

    # fitting regressor
    # rfc = RandomForestClassifier(n_estimators=30)
    rfc = ExtraTreesClassifier(
        # n_estimators=30,
        # max_features='sqrt'
    )

    # predict
    rfc.fit(X_scaled, rewards)
    # y_predict = rfc.predict(X_train)

    # saving
    sk.externals.joblib.dump(rfc, 'models/' + currency + '.pkl', compress=9)