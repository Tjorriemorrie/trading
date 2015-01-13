import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.cross_validation import cross_val_score
import sklearn as sk
from features import *
from os.path import isfile, join, realpath
from os import listdir, remove
import simplejson as json


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

    pathData = realpath('data/{0}'.format(currency.upper()))
    onlyfiles = sorted([f for f in listdir(pathData) if isfile(join(pathData, f))])
    data = {}
    for file in onlyfiles:
        with open(pathData + '/' + file, 'rb') as f:
            fileData = json.loads(f.read())
            if 'code' in fileData:
                print 'removed bad file', file
                remove(pathData + '/' + file)
            else:
                data = dict(data.items() + fileData.items())
    print 'data loaded'

    features = extractFeatures(data)
    print len(features), 'features extracted'
    print json.dumps(features[-1], indent=4)

    rewards = calcRewards(data)
    print len(rewards), 'rewards calculated'
    print json.dumps(rewards[-10:-5], indent=4)

    # split sets
    X_train, X_test, y_train, y_test = getSplit(features, rewards)
    print 'sets splitted'

    # fitting regressor
    # rfc = RandomForestClassifier(n_estimators=30)
    rfc = ExtraTreesClassifier(
        n_estimators=30,
        # max_features='sqrt',
    )
    rfc.fit(X_train, y_train)
    print 'fitted classifier'

    # saving
    sk.externals.joblib.dump(rfc, 'models/' + currency + '.pkl', compress=9)
    print 'saved model'