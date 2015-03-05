import logging
import argparse
import os
import numpy as np
from random import random, choice, shuffle, randint
from pprint import pprint
from time import time, sleep
import pickle
import pandas as pd
from main import loadData, loadQ, getBackgroundKnowledge, copyBatch, summarizeActions, calculateActions
from train import CURRENCIES, INTERVALS, PERIODS
from world import getState, getReward


def main(debug):
    interval = choice(INTERVALS)

    for currency, min_trail in CURRENCIES.iteritems():
        actions = calculateActions(min_trail)

        df = loadData(currency, interval)

        df = getBackgroundKnowledge(df, PERIODS)
        # print df
        # break

        q = loadQ(currency, interval)

        df_last = df[-1:]
        a = predict(df, q, PERIODS, actions)

        row = df_last.iloc[-1]
        logging.warn('{0} {1} {2}'.format(currency, row.name, a))


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