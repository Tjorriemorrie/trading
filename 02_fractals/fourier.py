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

    print 'selecting data...'
    lasthour = daily[-60:]['close'].as_matrix()
    print lasthour

    print 'creating fourier...'
    ft = np.fft.fft(lasthour)
    print ft

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(lasthour[2:-2], label='close', color='b')
    ax2 = ax1.twinx()
    ax2.plot(ft[2:-2], label='FFT', color='r')
    plt.show()
    break
























