import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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

    print 'loading daily...'
    daily = pd.read_csv(
        r'../' + currency + '1440.csv',
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        parse_dates=[[0, 1]],
        index_col=0,
    )

    # data = daily.as_matrix()
    # opens = data[:, 0].astype(float)
    # highs = data[:, 1].astype(float)
    # lows = data[:, 2].astype(float)
    # closes = data[:, 3].astype(float)
    # volumes = data[:, 4].astype(int)

    # print daily
    obv = []
    dayPrev = daily.irow(0)
    for datetime, day in daily.iterrows():
        diff = day['close'] - dayPrev['close']
        if 'JPY' in currency:
            diff /= 100
        obv.append(diff * day['volume'])
        dayPrev = day

    print len(obv), 'OBV'
    # print obv
    plt.plot(obv)
    plt.show()

    chunked = []
    tmp = 0
    for i, ob in enumerate(obv):
        # print ob
        tmp += ob
        if abs(tmp) >= 500:
            # print tmp
            chunked.append(tmp)
            tmp = 0
    print len(chunked), 'chunked'
    plt.plot(chunked)
    plt.show()

    grouped = []
    tmp = 0
    n = 500
    for i, chunk in enumerate(chunked):
        start = max(0, i - n)
        s = sum(obv[start:i])
        grouped.append(s / n)
    print len(grouped), 'grouped'
    plt.plot(grouped)
    plt.show()

    # break
