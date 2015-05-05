import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import choice
from features import FeatureFactory



def addMaxMins(df, n=2):
    '''
    get highs and lows for n periods backwards
    1 min = 1m
    2 min = 2m
    4 min = 4m
    8 min = 8m
    16 min = 16m
    32 min = 32m
    64 min = 1h 4m
    128 min = 2h 8m
    256 min = 4h 16m
    512 min = 8h 32m
    1024 min = 17h 4m
    '''
    print 'retrieving entry features...'

    columns = {}
    for i, row in df.iterrows():
        # row['max_1'] = row['high']
        # row['min_1'] = row['low']
        # print '\n\ni', i
        x = 1
        for y in xrange(1, n):
            # print 'x', x
            start = max(0, i+1 - x)
            # print 'start', start, ':', i+1
            slice = df[start:i+1]
            # print slice
            # print 'len', len(slice)
            
            if 'max_' + str(x) not in columns:
                columns['max_' + str(x)] = []
            if 'min_' + str(x) not in columns:
                columns['min_' + str(x)] = []
                
            columns['max_' + str(x)].append(max(slice['high']) / row['close'])
            columns['min_' + str(x)].append(min(slice['low']) / row['close'])
            # print '\n'
            x *= 2

            # break
        # break

    for name, vector in columns.iteritems():
        df[name] = vector


def processMaxMins(df):
    print 'processing max and mins...'



def addTradeSetUps(df):
    print 'adding trade set ups...'


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

intervals = [
    # '60',
    '1440',
]

if __name__ == '__main__':
    # randomly select currency (due to high iteration)
    currency = choice(currencies)
    interval = choice(intervals)
    print currency, interval

    print 'loading dataframe...'
    df = pd.read_csv(
        r'../data/' + currency + interval + '.csv',
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        # parse_dates=[[0, 1]],
        # index_col=0,
    )
    print df.tail()

    ff = FeatureFactory()

    # establish and calculate the trade set ups
    print '\n\nprocessing entries...'
    ff.getEntries(df)
    # print df

    # establish exits
    print '\n\nprocessing...'
    trades = ff.process(df)
    # print trades

    wins, losses = 0, 0
    tradeWon = None
    tradeLost = None
    for trade in trades:
        # print trade
        if trade['profit'] > 0:
            wins += 1
            tradeWon = trade
        else:
            losses += 1
            tradeLost = trade

    print 'wins', wins
    print 'losses', losses

    ff.showGraphs(df, tradeWon)
    ff.showGraphs(df, tradeLost)


