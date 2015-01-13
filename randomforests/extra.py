import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.cross_validation import cross_val_score
from features import FeatureFactory
import sklearn as sk
import operator

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


def ema(s, n):
    """ returns an n period exponential moving average for the time series s
    s is a list ordered from oldest (index 0) to most recent (index -1)
    n is an integer
    returns a numeric array of the exponential moving average """
    s = np.array(s).astype(float)
    ema = []
    j = 1

    # get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema[:0] = [sma] * n

    # EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (s[n] - sma) * multiplier) + sma)

    # now calculate the rest of the values
    for i in s[n + 1:]:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        ema.append(tmp)
        j = j + 1

    # print "ema length = " + str(len(ema))
    return ema


for currency in currencies:
    print '\n' + currency

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

    # calculating features
    print '\n calculating features...'
    ff = FeatureFactory()
    X_scaled = ff.getFeatures(opens, highs, lows, closes, volumes)
    # print X_scaled

    # set rewards
    # print '\ncalculating rewards...'
    rewards = ff.getRewards(closes)  # print rewards

    # train split
    # print '\nsplitting training set'
    X_train, X_test, y_train, y_test = ff.getSplit(X_scaled, rewards)

    # fitting regressor
    # print '\nfitting regressor'
    clf = ExtraTreesClassifier(
        # n_estimators=50,
        # criterion='gini',
        # max_features='auto',
        # max_depth=30,
        # min_samples_split=2,
        # min_samples_leaf=1,
        # max_leaf_nodes=None,
        # bootstrap=True,
        # n_jobs=1,
        # random_state=None,
        # verbose=0,
    )

    # scores
    # scores = cross_val_score(
    #     estimator=rfc,
    #     X=X_train,
    #     y=y_train,
    #     verbose=0,
    #     cv=10,
    # )
    # print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    # predict
    clf.fit(X_train, y_train)
    y_predict = clf.predict(X_train)
    longs = list(y_predict).count('long')
    shorts = list(y_predict).count('short')
    total = longs + shorts + 0.
    longRatio = longs / total
    shortRatio = shorts / total
    print('long/short: ' + str(int(longRatio * 100)) + ' / ' + str(int(shortRatio * 100)))

    # feature importances
    # print '\nFeature importances'
    # importances = {}
    # features = ff.getNames()
    # for feature, importance in zip(features, rfc.feature_importances_):
    # importances[feature.strip()] = importance
    # importances_sorted = sorted(importances.iteritems(), key=operator.itemgetter(1))
    # # print importances_sorted
    # for feature, importance in importances_sorted:
    # 	print feature + ' ' + str(int(importance * 1000))
    # print importances_sorted

    # saving
    sk.externals.joblib.dump(clf, 'models/' + currency + '.pkl', compress=9)

    # Plot the results
    import pylab as pl

    # pl.figure()
    # pl.scatter(xrange(len(closes)), closes, c="k", label="data")
    # pl.plot(xrange(len(closes)), y_predict, c="g", label="max_depth=1", linewidth=1)
    # # pl.plot(X_test, y_2, c="r", label="max_depth=2", linewidth=1)
    # # pl.plot(X_test, y_3, c="b", label="max_depth=3", linewidth=1)
    # pl.xlabel("data")
    # pl.ylabel("target")
    # pl.title("Decision Tree Regression")
    # pl.legend()
    # pl.show()