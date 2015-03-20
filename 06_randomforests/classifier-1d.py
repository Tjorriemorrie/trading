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

    # train split
    # print '\nsplitting training set'
    X_train, X_test, y_train, y_test = ff.getSplit(X_scaled, rewards, 0)

    # fitting regressor
    # rfc = RandomForestClassifier(n_estimators=30)
    rfc = ExtraTreesClassifier(
        n_estimators=30,
        # max_features='sqrt'
    )

    # scores
    scores = cross_val_score(
        estimator=rfc,
        X=X_test,
        y=y_test,
        verbose=0,
        cv=2,
    )
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    # predict
    rfc.fit(X_train, y_train)
    # y_predict = rfc.predict(X_train)

    # saving
    sk.externals.joblib.dump(rfc, 'models/' + currency + '.pkl', compress=9)