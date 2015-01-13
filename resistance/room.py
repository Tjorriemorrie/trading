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
    # r'../EURJPY1440.csv',
    # r'../EURGBP1440.csv',
    # r'../AUDUSD1440.csv',
    names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
)

print '\nData'
data = df.as_matrix()
# data = data[-1000:]
print data

opens = data[:, 2].astype(float)
highs = data[:, 3].astype(float)
lows = data[:, 4].astype(float)
closes = data[:, 5].astype(float)

print '\nCloses'
print closes

# count days that high is highest
levels = {}
i = 0
cutOff = 100001
for open, high, low, close in zip(opens, highs, lows, closes):

    # high
    pip = round(high, 4)
    pos = 0
    highestForward = True
    highestBackward = True
    while highestForward and highestBackward:
        pos += 1
        # test if data in key
        if i - pos < 0 or i + pos >= len(closes) or pos >= cutOff:
            break
        highestForward = True if highs[i + pos] < pip else False
        highestBackward = True if highs[i - pos] < pip else False

    pips = np.arange(round(max(open, close), 4), round(high, 4), 0.0001)
    for pip in pips:
        if pip not in levels:
            levels[pip] = 0.
        levels[pip] += pos - 1

    # low
    pip = round(low, 4)
    pos = 0
    lowestForward = True
    lowestBackward = True
    while lowestForward and lowestBackward:
        pos += 1
        # test if data in key
        if i - pos < 0 or i + pos >= len(closes) or pos >= cutOff:
            break
        lowestForward = True if lows[i + pos] > pip else False
        lowestBackward = True if lows[i - pos] > pip else False

    pips = np.arange(round(min(open, close), 4), round(low, 4), 0.0001)
    for pip in pips:
        if pip not in levels:
            levels[pip] = 0.
        levels[pip] += pos - 1

    i += 1

print '\n levels'
# print levels

# scale
print '\nScaling values'
levelsMin = min(levels.values())
levelsMax = max(levels.values())
for pip, weight in levels.iteritems():
    levels[pip] = (weight - levelsMin) / (levelsMax - levelsMin)
print 'min = ' + str(levelsMin)
print 'max = ' + str(levelsMax)

print '\n levels scaled'
# print np.asarray(levels)



# Plot the results
import pylab as pl

plotLast = min(len(data), 10000)
closesToShow = closes[-plotLast:]
cutOff = 0.01
margin = 0.0100

pl.figure(figsize=(19, 11))
pl.plot(xrange(plotLast), closesToShow, c="k", label="data")
pl.ylim(min(closesToShow) - margin, max(closesToShow) + margin)
for pip, weight in levels.iteritems():
    if weight < cutOff:
        continue
    # print 'line at ' + str(pip)
    pl.axhline(pip, color=(0, 0, 0, weight), linewidth=1)
# pl.plot(xrange(len(closes)), y_predict, c="g", label="max_depth=1", linewidth=1)
# pl.plot(X_test, y_2, c="r", label="max_depth=2", linewidth=1)
# pl.plot(X_test, y_3, c="b", label="max_depth=3", linewidth=1)

pl.xlabel("data")
pl.ylabel("target")
pl.title("Resistance levels")
pl.legend()
pl.show()