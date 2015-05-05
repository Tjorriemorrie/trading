import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import choice
from features import FeatureFactory
from types import *


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

    # trades
    trades = []
    # entry
    entry = None
    iEntry = None
    # low - start
    low = None
    iLow = None
    # high - mid
    high = None
    iHigh = None
    # exit
    exit = None
    iExit = None
    # process
    trade = {}
    for i, row in df.iterrows():

        # look for entry
        if not entry:

            # LOW
            # if none: assign
            if isinstance(low, NoneType):
                low = row
                iLow = i
                print 'low new', low['low']
            # else: if lower than low: new low & invalid high
            elif row['low'] < low['low']:
                low = row
                iLow = i
                high = None
                iHigh = None
                print 'low lower', low['low']
            # else if lower too old then update

            # HIGH
            # if we have a low, and it's the lowest thus far, then get the high
            # high must be at least 5 ticks later
            elif i - iLow < 5:
                trade['low'] = low
                trade['iLow'] = iLow
                continue
            # if none: assign
            elif isinstance(high, NoneType):
                high = row
                iHigh = i
                print 'high new', high['high']
            # else: if higher than high: new high
            elif row['high'] > high['high']:
                high = row
                iHigh = i
                print 'high higher', high['high']

            # CURRENT
            # can enter if close is at least 5 ticks later
            elif i - iHigh < 5:
                trade['high'] = high
                trade['iHigh'] = iHigh
                continue
            # if we have a low, and if we have a high, then we can look for entry
            else:
                range = abs(high['high'] - low['low'])
                m50 = high['high'] - (range * 0.500)
                m61 = high['high'] - (range * 0.618)
                t38 = high['high'] + (range * 0.382)

                print '\nclose', row['close']
                print 'low', low['low']
                print 'high', high['high']
                print 'range', range
                print 'm50', m50
                print 'm61', m61
                print 't38', t38

                # if close is in good range: 50 < C < 61, then enter
                if m50 < row['close'] < m61:
                    entry = row
                    iEntry = i
                    print 'entry', entry['close']

        # look for exit
        else:
            # let it turn for at least 5 ticks
            if i - iEntry < 5:
                trade['entry'] = entry
                trade['iEntry'] = iEntry
                continue

            # stop loss if lower than m61
            # take profit if higher than t38
            elif row['close'] > t38 or row['close'] < m61:
                trade['exit'] = row
                trade['iExit'] = i
                trade['profit'] = exit['close'] - entry['close']
                trades.append(trade)
                trade = {}


    print len(trades)
    print trades