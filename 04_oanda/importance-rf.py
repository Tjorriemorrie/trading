import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score
import sklearn as sk
import collections as col
import operator
from features import *
from random import shuffle


currencies = [
    # 'AUDUSD',
    # 'EURGBP',
    # 'EURJPY',
    'EURUSD',
    # 'GBPJPY',
    # 'GBPUSD',
    # 'NZDUSD',
    # 'USDCAD',
    # 'USDCHF',
    # 'USDJPY',
]
shuffle(currencies)

for currency in currencies:

    print '\n' + currency

    model = 'models/{0}.pkl'.format(currency.upper())
    rfc = sk.externals.joblib.load(model)

    # feature importances
    names = getNames()
    importances = rfc.feature_importances_
    stds = np.std([tree.feature_importances_ for tree in rfc.estimators_], axis=0)
    print len(names), names
    print len(importances), importances
    print len(stds), stds

    indices = np.argsort(importances)[::-1]
    print indices

    for i in indices:
        print("%d. %s = %s (%s)" % (i, names[i], round(importances[i], 2), round(stds[i], 2)))

    plt.figure()
    plt.title(currency)
    plt.bar(range(len(importances)), importances[indices],
           color="r", yerr=stds[indices], align="center")
    plt.xticks(range(len(importances)), indices)
    plt.xlim([-1, len(importances)])
    plt.show()

    # ordered = {}
    # for feature, importance in zip(features, importances):
    #     ordered[feature.strip()] = importance
    # importances_sorted = sorted(ordered.iteritems(), key=operator.itemgetter(1))
    # # # print importances_sorted
    # for feature, importance in importances_sorted:
    #     print feature + ' ' + str(importance)
    # # # print importances_sorted
    # #

    break