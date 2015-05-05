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

    dailySubs = np.array_split(daily, 500)
    logs = []
    for daily in dailySubs:

        mean = daily['close'].mean()
        # print 'mean = ' + str(mean)

        daily['mas'] = [close - mean for close in daily['close']]
        # print daily

        daily['cumsum'] = daily['mas'].cumsum()
        # print daily

        range = daily['cumsum'].max() - daily['cumsum'].min()
        # print 'range = ' + str(range)

        std = daily['close'].std()
        # print 'std = ' + str(std)

        rs = range / std
        # print 'rescaled range = ' + str(rs)

        log = np.log(rs)
        # print 'log = ' + str(log)

        logs.append(log)

    plt.plot(logs)
    plt.show()
    break
