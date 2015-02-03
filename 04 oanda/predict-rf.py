import pandas as pd
import numpy as np
import sklearn as sk
from features import *
from simplejson import json

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

same = []
changed = []
for currency in currencies:
    # print '\n' + currency

    model = 'models/{0}.pkl'.format(currency.upper())
    rfc = sk.externals.joblib.load(model)

    pathData = realpath('data/{0}'.format(currency.upper()))
    onlyfiles = sorted([f for f in listdir(pathData) if isfile(join(pathData, f))])
    data = {}
    for file in onlyfiles:
        with open(pathData + '/' + file, 'rb') as f:
            fileData = json.loads(f.read())
            data = dict(data.items() + fileData.items())
    print 'data loaded'

    features = extractFeatures(data)
    print len(features), 'features extracted'
    print json.dumps(features[-1], indent=4)

    rewards = calcRewards(data)
    print len(rewards), 'rewards calculated'
    print json.dumps(rewards[-10:-5], indent=4)

    # split sets
    X_train, X_test, y_train, y_test = sk.cross_validation.train_test_split(
        features,
        rewards,
        test_size=0.30,
        # random_state=0,
    )
    print 'sets splitted'

    # recent
    X_yesterday = X_scaled[-2:-1]
    X_today = X_scaled[-1:]

    # predict
    p_yesterday = rfc.predict(X_yesterday)[0]
    p_today = rfc.predict(X_today)[0]

    if p_yesterday == p_today:
        print data[-1:][0][0] + ' - ' + str(p_today) + ' - ' + currency
    else:
        print data[-1:][0][0] + ' - ' + str(p_today) + ' - ' + currency + ' <--!'
