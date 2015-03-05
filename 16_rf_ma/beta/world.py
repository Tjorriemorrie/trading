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
        current = row['close']
        logging.debug('Reward: {0} {1} {2:.4f} stop {3:.4f}'.format(a_trade, i, current, take))
        # buy
        if a_trade == 'buy':
            # exit?
            if current < take:
                logging.debug('Reward: take profit triggered: current [{0:.4f}] < take [{1:.4f}]'.format(current, take))
                r += current - entry
                break
            # new high?
            if current + trail > take:
                logging.debug('Reward: new high: current [{0:.4f}] + trail [{1:0.4f}] > take [{2:.4f}]'.format(current, trail, take))
                take = current + trail
        # sell
        if a_trade == 'sell':
            # exit?
            if current > take:
                logging.debug('Reward: take profit triggered: current [{0:.4f}] > take [{1:.4f}]'.format(current, take))
                r += entry - take
                break
            # new low?
            if current + trail < take:
                logging.debug('Reward: new low: current [{0:.4f}] + trail [{1:0.4f}] < take [{2:.4f}]'.format(current, trail, take))
                take = current + trail

    r -= ticks / pip_mul

    return r, ticks
