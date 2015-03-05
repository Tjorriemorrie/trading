import logging
import numpy as np
import argparse
from random import random, choice, shuffle, randint
from pprint import pprint
from time import time, sleep
import pandas as pd


def getState(df, periods):
    logging.info('State: periods {0}...'.format(periods))

    s = []
    row = df.iloc[0]

    for x in periods:
        s.append(1 if row['ma_{0}_bullish'.format(x)] else 0)
        s.append(1 if row['ma_{0}_divergence'.format(x)] else 0)
        s.append(1 if row['ma_{0}_magnitude'.format(x)] else 0)

        for y in periods:
            if y <= x:
                continue
            s.append(1 if row['ma_{0}_crossover_{1}_bullish'.format(x, y)] else 0)
            s.append(1 if row['ma_{0}_crossover_{1}_divergence'.format(x, y)] else 0)
            s.append(1 if row['ma_{0}_crossover_{1}_magnitude'.format(x, y)] else 0)
    logging.debug('State: moving average {0}'.format(s))

    return s


def getReward(df, a, pip_mul):
    a_trade, a_trailing = a.split('-')
    logging.info('Reward: {0} with {1} stoploss'.format(a_trade, a_trailing))

    entry = df.iloc[0]['close']
    logging.debug('Reward: entry at {0:.4f}'.format(entry))
    if a_trade == 'buy':
        trail = -(float(a_trailing) / pip_mul)
    else:
        trail = (float(a_trailing) / pip_mul)
    take = entry + trail
    logging.debug('Reward: trail at {0:.4f}'.format(trail))

    ticks = -1
    r = 0
    for i, row in df.iterrows():
        ticks += 1
        logging.debug('Reward: {0} {1} {2:.4f} stop {3:.4f}'.format(a_trade, i, current_close, take))
        # buy
        if a_trade == 'buy':
            # exit?
            if row['low'] < take:
                logging.debug('Reward: take profit triggered: current [{0:.4f}] < take [{1:.4f}]'.format(current_close, take))
                r += take - entry
                break
            # new high?
            if row['high'] + trail > take:
                logging.debug('Reward: new high: current [{0:.4f}] + trail [{1:0.4f}] > take [{2:.4f}]'.format(current_close, trail, take))
                take = row['high'] + trail
        # sell
        if a_trade == 'sell':
            # exit?
            if row['high'] > take:
                logging.debug('Reward: take profit triggered: current [{0:.4f}] > take [{1:.4f}]'.format(current_close, take))
                r += entry - take
                break
            # new low?
            if row['low'] + trail < take:
                logging.debug('Reward: new low: current [{0:.4f}] + trail [{1:0.4f}] < take [{2:.4f}]'.format(current_close, trail, take))
                take = row['low'] + trail

    r -= ticks / pip_mul

    return r, ticks
