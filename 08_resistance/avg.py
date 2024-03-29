import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import cross_val_score
import sklearn as sk
import collections as col


# load data
df = pd.read_csv(
    r'../EURUSD1440.csv',
    names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
)

data = df.as_matrix()
data = data[-100:]
print data

opens = data[:, 2].astype(float)
highs = data[:, 3].astype(float)
lows = data[:, 4].astype(float)
closes = data[:, 5].astype(float)


levels = col.OrderedDict()

print '\nCloses'
print closes

# calculate shadows
# topShadows = [high - max(open, close) for open, high, close in zip(opens, highs, closes)]
# topShadowsMean = np.mean(topShadows)
for open, high, low, close in zip(opens, highs, lows, closes):

    # HIGH
    pips = np.arange(round(max(open, close), 4), round(high, 4), 0.0001)
    # print '\nTmp'
    # print tmp

    percentiles = [sp.stats.percentileofscore(pips, key) for key in pips]
    # print '\npercentiles'
    # print percentiles

    for pip, percentile in zip(pips, percentiles):
        pip = round(pip, 4)
        if pip in levels:
            levels[pip] = int((levels[pip] + int(round(percentile))))
        else:
            levels[pip] = int(round(percentile))

    # LOW
    pips = np.arange(round(low, 4), round(min(open, close), 4), 0.0001)
    # print '\nTmp'
    # print tmp

    percentiles = [sp.stats.percentileofscore(pips, key) for key in pips]
    # print '\npercentiles'
    # print percentiles

    for pip, percentile in zip(pips, percentiles):
        pip = round(pip, 4)
        if pip in levels:
            # print str(pip) + ' exists'
            levels[pip] = int((levels[pip] + int(round(percentile))))
        else:
            # print str(pip) + ' new'
            levels[pip] = int(round(percentile))

    # decay
    # for level in levels:
    #     level *= 0.5


#scale
levels = sk.preprocessing.MinMaxScaler().fit_transform(levels)

print '\n levels'
print levels


# Plot the results
import pylab as pl
plotLast = min(len(data), 100)
closesToShow = closes[-plotLast:]
cutOff = 0
margin = 0.0100

pl.figure(figsize=(19, 11))
pl.plot(xrange(plotLast), closesToShow, c="k", label="data")
pl.ylim(min(closesToShow)-margin, max(closesToShow)+margin)
for pip, weight in levels.iteritems():
    if weight < cutOff:
        continue
    # print 'line at ' + str(pip)
    pl.axhline(pip, color=(0, 0, 0, weight/100.), linewidth=0.1)
# pl.plot(xrange(len(closes)), y_predict, c="g", label="max_depth=1", linewidth=1)
# pl.plot(X_test, y_2, c="r", label="max_depth=2", linewidth=1)
# pl.plot(X_test, y_3, c="b", label="max_depth=3", linewidth=1)

pl.xlabel("data")
pl.ylabel("target")
pl.title("Resistance levels")
pl.legend()
pl.show()