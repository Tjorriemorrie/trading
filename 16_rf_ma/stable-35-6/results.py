import logging
import argparse
import os
import numpy as np
from random import random, choice, shuffle, randint
from pprint import pprint
from time import time, sleep
import pickle
import pandas as pd
from main import loadData, loadQ, getBackgroundKnowledge, calculateActions
from train import CURRENCIES, INTERVALS, PERIODS


def main(debug):
    interval = choice(INTERVALS)

    for currency, min_trail in CURRENCIES.iteritems():
        pip_mul = 100. if 'JPY' in currency else 10000.
        actions = calculateActions(min_trail)

        df = loadData(currency, interval)
        df = df[-2000:]

        df = getBackgroundKnowledge(df, PERIODS)
        # print df
        # break

        q = loadQ(currency, interval)

        rewards = []
        errors = []
        ticks = []
        for x in xrange(1000):
            index_start = randint(0, len(df)-1)
            df_inner = df.iloc[index_start:]
            q, r, error, tick = test(df_inner, q, PERIODS, actions, pip_mul)

            # results
            rewards.append(r)
            errors.append(error * pip_mul)
            ticks.append(tick)

        # RMSD
        rmsd = np.sqrt(np.mean([e**2 for e in errors]))

        # win ratio
        wins = [1. if r > 0. else 0. for r in rewards]

        logging.warn('{0} RMSD {2:03d} PPT {3:03d} WR {5:.0f}% [ticks:{6:.1f} sum:{4:.1f}]'.format(
            currency,
            None,
            int(rmsd),
            int(np.mean(rewards) * pip_mul),
            sum(rewards),
            np.mean(wins) * 100,
            np.mean(ticks),
        ))



########################################################################################################
# WORLD
########################################################################################################

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
        logging.debug('Reward: {0} {1} {2:.4f} stop {3:.4f}'.format(a_trade, i, row['close'], take))
        # buy
        if a_trade == 'buy':
            # exit?
            if row['low'] < take:
                logging.debug('Reward: take profit triggered: low [{0:.4f}] < take [{1:.4f}]'.format(row['low'], take))
                r += take - entry
                break
            # new high?
            if row['high'] + trail > take:
                logging.debug('Reward: new high: high [{0:.4f}] + trail [{1:0.4f}] > take [{2:.4f}]'.format(row['high'], trail, take))
                take = row['high'] + trail
        # sell
        if a_trade == 'sell':
            # exit?
            if row['high'] > take:
                logging.debug('Reward: take profit triggered: high [{0:.4f}] > take [{1:.4f}]'.format(row['high'], take))
                r += entry - take
                break
            # new low?
            if row['low'] + trail < take:
                logging.debug('Reward: new low: low [{0:.4f}] + trail [{1:0.4f}] < take [{2:.4f}]'.format(row['low'], trail, take))
                take = row['low'] + trail

    r -= ticks / pip_mul

    return r, ticks



########################################################################################################
# SARSA
########################################################################################################

def test(df, q, periods, actions, pip_mul):
    logging.info('Testing: started...')

    # initial state
    s = getState(df, periods)

    # initial action
    a = getAction(q, s, 0, actions)

    # get reward
    r, ticks = getReward(df, a, pip_mul)

    # get delta
    d = getDelta(q, s, a, r)

    return q, r, d, ticks


def getAction(q, s, epsilon, actions):
    logging.info('Action: finding...')

    # exploration
    if random() < epsilon:
        logging.debug('Action: explore (<{0:.2f})'.format(epsilon))
        a = choice(actions)

    # exploitation
    else:
        logging.debug('Action: exploit (>{0:.2f})'.format(epsilon))
        q_max = None
        for action in actions:
            q_sa = q.get((tuple(s), action), random() * 10.)
            logging.debug('Qsa action {0} is {1:.4f}'.format(action, q_sa))
            if q_sa > q_max:
                q_max = q_sa
                a = action

    logging.info('Action: found {0}'.format(a))
    return a


def getDelta(q, s, a, r):
    logging.info('Delta: calculating...')
    q_sa = q.get((tuple(s), a), 0)
    logging.debug('Delta: r [{0:.4f}] - Qsa [{1:0.4f}]'.format(r, q_sa))
    d = r - q_sa
    logging.info('Delta: {0:.4f}'.format(d))
    return d


def updateQ(q, s, a, d, r, alpha):
    logging.info('Q: updating learning at {0:.2f}...'.format(alpha))

    # update q
    sa = (tuple(s), a)
    q_sa = q.get(sa, r)
    logging.debug('Q: before {0:.4f}'.format(q_sa))
    q_sa_updated = q_sa + (alpha * d)
    q[sa] = q_sa_updated
    logging.debug('Q: after {0:.4f}'.format(q_sa, q_sa_updated))

    return q


########################################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-vv', '--very_verbose', action='store_true')
    args = parser.parse_args()

    verbose = args.verbose
    very_verbose = args.very_verbose
    lvl = logging.DEBUG if very_verbose else (logging.INFO if verbose else logging.WARN)

    logging.basicConfig(
        level=lvl,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    debug = verbose or very_verbose

    main(debug)