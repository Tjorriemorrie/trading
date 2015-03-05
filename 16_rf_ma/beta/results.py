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
from world import getState, getReward


def main(debug):
    interval = choice(INTERVALS)

    for currency, min_trail in CURRENCIES.iteritems():
        pip_mul = 100. if 'JPY' in currency else 10000.
        actions = calculateActions(min_trail)

        df = loadData(currency, interval)

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