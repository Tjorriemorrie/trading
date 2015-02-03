import pandas as pd
import numpy as np
import sklearn as sk
from features import FeatureFactory

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

same = []
changed = []
for currency in currencies:
    # print '\n' + currency

    # load data
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

    rfc = sk.externals.joblib.load('models/' + currency + '.pkl')

    # calculating features
    # print '\n calculating features...'
    ff = FeatureFactory()
    X_scaled = ff.getFeatures(opens, highs, lows, closes, volumes)

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
