import logging
import argparse
import os
import pickle
import pandas as pd
import numpy as np
from prettytable import PrettyTable
from random import random, choice, shuffle, randint
from pprint import pprint
from time import time, sleep
from main import loadData, loadQ, getBackgroundKnowledge, summarizeActions, calculateActions
from world import DATA, PERIODS, getState, getReward


def main(equity, debug):
    pips = []
    pt = PrettyTable(['Currency', 'min trail', 'date', '1', '2', '3', '4', '5'])
    for info in DATA:
        currency = info['currency']
        min_trail = info['trail']
        interval = info['intervals'][0]
        pip_mul = info['pip_mul']
        logging.warn('{0}...'.format(currency))

        actions = calculateActions(min_trail)

        df = loadData(currency, interval)

        df = getBackgroundKnowledge(df, PERIODS)
        # print df
        # break

        q = loadQ(currency, interval)

        df_last = df[-1:]
        row = df_last.iloc[-1]
        predictions = predict(df, q, PERIODS, actions, pip_mul, row)

        # logging.warn('{0} {1} {2}'.format(currency, row.name, a))
        pt.add_row([currency, min_trail, str(row.name).split(' ')[0]] + predictions)

        pips.append(int(predictions[0].split(' ')[0].split('-')[1]))

    print pt

    equity = float(equity)
    risk = 0.10
    available = equity * risk
    logging.info('Risk ${0:.0f} from ${1:.0f} at {2:.0f}%'.format(available, equity, risk * 100))

    total_pips = sum(pips)
    lot_size = available / total_pips
    lot_size /= len(pips)
    logging.warn('Lot size = {0:.2f}'.format(lot_size))



########################################################################################################
# SARSA
########################################################################################################

def predict(df, q, periods, actions, pip_mul, row):
    logging.info('Predict: started...')

    # state
    s = getState(df, periods)

    # get top actions
    predictions = []
    for n in xrange(5):
        a, q_sa = getAction(q, s, 0, actions)
        a_trade, a_trail = a.split('-')
        if a_trade == 'buy':
            stop_loss = row['close'] - (float(a_trail) / pip_mul)
        else:
            stop_loss = row['close'] + (float(a_trail) / pip_mul)
        predictions.append('{0} [{1:.4f}] SL:{2:0.4f}'.format(a, q_sa, stop_loss))
        logging.info('{0} action = {1}'.format(n, a))
        actions.remove(a)

    return predictions


def getAction(q, s, epsilon, actions):
    logging.info('Action: finding...')

    # exploration
    if random() < epsilon:
        logging.debug('Action: explore (<{0:.2f})'.format(epsilon))
        a = choice(actions)
        q_max = None

    # exploitation
    else:
        logging.debug('Action: exploit (>{0:.2f})'.format(epsilon))
        q_max = None
        for action in actions:
            q_sa = q.get('|'.join([s, action]), random() * 10.)
            logging.debug('Qsa action {0} is {1:.4f}'.format(action, q_sa))
            if q_sa > q_max:
                q_max = q_sa
                a = action

    logging.info('Action: found {0}'.format(a))
    return a, q_max


def getDelta(q, s, a, r):
    logging.info('Delta: calculating...')
    q_sa = q.get('|'.join([s, a]), 0)
    logging.debug('Delta: r [{0:.4f}] - Qsa [{1:0.4f}]'.format(r, q_sa))
    d = r - q_sa
    logging.info('Delta: {0:.4f}'.format(d))
    return d


########################################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('equity')
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

    main(args.equity, debug)