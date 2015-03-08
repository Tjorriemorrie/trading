import logging
import argparse
import os
import numpy as np
from random import random, choice, shuffle, randint
from pprint import pprint
from time import time, sleep
import pickle
import pandas as pd
from main import loadData, getBackgroundKnowledge, copyBatch, summarizeActions, calculateActions
from train import CURRENCIES, INTERVALS, PERIODS


def main(debug):
    interval = choice(INTERVALS)

    for currency, min_trail in CURRENCIES.iteritems():
        pip_mul = 100. if 'JPY' in currency else 10000.
        actions = calculateActions(min_trail)

        df = loadData(currency, interval)
        df = df[-1000:]

        df = getBackgroundKnowledge(df, PERIODS)
        # print df
        # break

        q = loadQ(currency, interval)

        df_last = df[-1:]
        a = predict(df, q, PERIODS, actions)

        row = df_last.iloc[-1]

        a_trade, a_trail = a.split('-')
        if a_trade == 'buy':
            stop_loss = row['close'] - (float(a_trail) / pip_mul)
        else:
            stop_loss = row['close'] + (float(a_trail) / pip_mul)

        logging.warn('{0} {1} a:{2} t:{3} sl:{4:.4f}'.format(
            row.name,
            currency,
            a_trade,
            a_trail,
            stop_loss,
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


def getReward(df, a):
    a_trade, a_trailing = a.split('-')
    logging.info('Reward: {0} with {1} stoploss'.format(a_trade, a_trailing))

    entry = df.iloc[0]['close']
    logging.debug('Reward: entry at {0:.4f}'.format(entry))
    if a_trade == 'buy':
        trail = -(float(a_trailing) / 10000.)
    else:
        trail = (float(a_trailing) / 10000.)
    take = entry + trail
    logging.debug('Reward: trail at {0:.4f}'.format(trail))

    r = None
    for i, row in df.iterrows():
        current = row['close']
        logging.debug('Reward: {0} {1} {2:.4f} stop {3:.4f}'.format(a_trade, i, current, take))
        # buy
        if a_trade == 'buy':
            # exit?
            if current < take:
                logging.debug('Reward: take profit triggered: current [{0:.4f}] < take [{1:.4f}]'.format(current, take))
                r = current - entry
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
                r = entry - take
                break
            # new low?
            if current + trail < take:
                logging.debug('Reward: new low: current [{0:.4f}] + trail [{1:0.4f}] < take [{2:.4f}]'.format(current, trail, take))
                take = current + trail

    if r:
        logging.info('Reward: {0:.4f}'.format(r))
    else:
        logging.info('Reward: None')
    return r



########################################################################################################
# SARSA
########################################################################################################

def predict(df, q, periods, actions):
    logging.info('Predict: started...')

    # state
    s = getState(df, periods)

    # initial action
    a = getAction(q, s, 0, actions)

    return a


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


def loadQ(currency, interval):
    logging.info('Q: loading...')
    try:
        with open('{0}/models/{1}_{2}.q'.format(os.path.realpath(os.path.dirname(__file__)), currency, interval), 'rb') as f:
            q = pickle.load(f)
    except (IOError, EOFError) as e:
        logging.error('Could not load Q for {0}'.format(currency))
        q = {}
    logging.info('Q: loaded {0}'.format(len(q)))
    return q


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