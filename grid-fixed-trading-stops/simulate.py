import pandas as pd
import numpy as np
from random import choice
from pprint import pprint


currencies = [
    'AUDUSD',
    'EURGBP',
    # 'EURJPY',
    'EURUSD',
    # 'GBPJPY',
    'GBPUSD',
    'NZDUSD',
    'USDCAD',
    'USDCHF',
    # 'USDJPY',
]


trades = 1000
results = {}
for currency in currencies:
    print '\n\n', currency
    factor = 10000.

    df = pd.read_csv(
        r'../data/' + currency + '1440.csv',
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        dtype={'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float', 'volume': 'int'}
    )
    df['range'] = df['high'] - df['low']
    print df.tail()

    # create grid
    mean = df['range'].mean()
    levels = [
        mean * 0.5,
        mean * 1.,
        mean * 1.5,
        mean * 2.,
        mean * 2.5,
    ]
    takeProfit = max(levels) + min(levels)
    gridProfit = sum([takeProfit - l for l in levels])
    gridLoss = sum([l + max(levels) for l in levels])
    print [l + max(levels) for l in levels]
    print 'mean', mean
    print 'Profit @', gridProfit
    print 'Loss @', gridLoss

    outcomes = []
    drawdown = 0
    for i in xrange(trades):
        print '\nTest', i

        # get sample
        iStart = choice(df.index)
        sample = df.iloc[iStart:]
        close = sample.iloc[0]['close']
        print iStart, '@', close

        longs = []
        shorts = []
        for adj in levels:
            longs.append({
                'active': False,
                'adj': round(adj, 4),
                'entry': round(close + adj, 4),
                'stop': round(close - gridLoss, 4),
                'profit': round(close + gridProfit, 4)
            })
            shorts.append({
                'active': False,
                'adj': round(-adj, 4),
                'entry': round(close - adj, 4),
                'stop': round(close + gridLoss, 4),
                'profit': round(close - gridProfit, 4)
            })

        # print 'longs'
        # pprint(longs)
        # print 'shorts'
        # pprint(shorts)
        # break

        for ii, d in sample.iterrows():
            # calculate net for today from scratch
            net = 0
            opened = 0

            # check entries
            for long in longs:
                # print d['high']
                # print long['entry']
                # print d['high'] >= long['entry']
                if not long['active'] and d['high'] >= long['entry']:
                    long['active'] = True
                    print d['date'], 'LONG entered', long['adj']
                elif long['active']:
                    opened += 1
                    net += d['close'] - long['entry']
            for short in shorts:
                if not short['active'] and d['low'] <= short['entry']:
                    short['active'] = True
                    print d['date'], 'SHORT entered', short['adj']
                elif short['active']:
                    net += short['entry'] - d['close']
                    opened += 1

            # print d['date'], 'CLOSE', d['close'], 'NET', round(net, 4)

            # check exit
            if opened >= len(levels) * 2 and net >= gridProfit:
                print d['date'], 'CONFLICT'
                break
            elif net >= gridProfit:
                print d['date'], 'WIN'
                outcomes.append(gridProfit)
                break
            elif opened >= len(levels) * 2:
                print d['date'], 'LOSS'
                outcomes.append(net)
                break

    print '\n', currency
    profit = round(sum(outcomes), 4)
    print 'Total profit', profit
    wins = [1. for o in outcomes if o > 0]
    ratio = sum(wins) / len(outcomes) * 100.
    print 'Win ratio', int(ratio), '%'

    results[currency] = {
        # 'outcomes': outcomes,
        'profit': profit,
        'ratio': ratio,
    }


# pprint(results)
print '\n\n'
print trades, 'total trades'
total = 0
for currency, stats in results.iteritems():
    print currency, 'profit', stats['profit'], 'ratio', int(stats['ratio'])
    total += stats['profit']

print '\nProfit per trade', round(total / (len(results) * trades), 4)

