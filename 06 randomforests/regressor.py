import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import cross_val_score
import sklearn as sk


df = pd.read_csv(
    r'../EURUSD1440.csv',
    names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
)

data = df.as_matrix()


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


# calculating features
print '\n calculating features...'
closes = data[:, 5].astype(float)
ema05s = ema(closes, 5)
ema08s = ema(closes, 8)
ema13s = ema(closes, 13)
ema21s = ema(closes, 21)
ema34s = ema(closes, 34)
ema5vs = ema(data[:, 6], 5)
ema8vs = ema(data[:, 6], 8)
X = np.array([[close/ema05, close/ema08, close/ema13, close/ema21, close/ema34, ema5v/ema8v]
     for close, ema05, ema08, ema13, ema21, ema34, ema5v, ema8v,
     in zip(closes, ema05s, ema08s, ema13s, ema21s, ema34s, ema5vs, ema8vs)
])
# print X
X_scaled = sk.preprocessing.scale(X)
# print X_scaled


# set rewards
print '\ncalculating rewards...'
rewards = []
iMax = 5 * 2
for pos, close in enumerate(closes):
    tmp = []
    for i in xrange(iMax):
        index = pos + i
        if index >= len(closes) - 2:
            break
        tmp.append(closes[index] - close)
    if len(tmp) > 0:
        reward = round(sum(tmp) / len(tmp) * 10000)
        rewards.append(reward)
    else:
        rewards.append(0)
# print rewards
rewards = np.asarray(rewards).astype(int)


# train split
print '\nsplitting training set'
X_train, X_test, y_train, y_test = sk.cross_validation.train_test_split(
    X_scaled,
    rewards,
    test_size=0.4,
    random_state=1,
    dtype=float,
)
print 'X-train: ' + str(X_train.shape)
print 'y-train: ' + str(y_train.shape)
print 'X-test: ' + str(X_test.shape)
print 'y-test: ' + str(y_test.shape)


# fitting regressor
print '\nfitting'
rfr = RandomForestRegressor(
    n_estimators=10,
    max_features='auto',
    criterion='mse',
    max_depth=None,
)
rfr.fit(X_train, y_train)


# scores
print '\nScores'
scores = cross_val_score(
    estimator=rfr,
    X=X_test,
    y=y_test,
    verbose=1,
    cv=10,
    n_jobs=4,
)
print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

