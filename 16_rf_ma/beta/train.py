import logging
import numpy as np
import argparse
from random import random, choice, shuffle, randint
from pprint import pprint
from time import time, sleep
import pandas as pd
from main import loadData, loadQ, saveQ, getBackgroundKnowledge, copyBatch, summarizeActions, calculateActions
from world import getState, getReward


CURRENCIES = {
    'AUDUSD': 40,
    'EURGBP': 50,
    'EURUSD': 30,
    'EURJPY': 100,
    'GBPUSD': 30,
    'GBPJPY': 150,
    'NZDUSD': 40,
    'USDCAD': 40,
    'USDCHF': 40,
    'USDJPY': 30,
}

INTERVALS = [
    # '60',
    '1440',
]

PERIODS = [3, 5, 8, 13, 21]


def main(debug):
    interval = choice(INTERVALS)

    minutes = 0
    while True:
        minutes += 1
        seconds_to_run = 60 * minutes
        seconds_info_intervals = seconds_to_run / 5
        logging.error('Training each currency for {0} minutes'.format(minutes))

        # shuffle(CURRENCIES)
        for currency, min_trail in CURRENCIES.iteritems():
            pip_mul = 100. if 'JPY' in currency else 10000.
            actions = calculateActions(min_trail)

            df = loadData(currency, interval)

            df = getBackgroundKnowledge(df, PERIODS)
            # print df
            # break

            alpha = 0.01
            epsilon = alpha * 2.
            q = loadQ(currency, interval)

            time_start = time()
            time_interval = seconds_info_intervals

            epoch = 0
            rewards = []
            errors = []
            ticks = []
            logging.warn('Training {0} on {1} with {2} ticks...'.format(currency, interval, len(df)))
            while True:
                epoch += 1
                logging.info(' ')
                logging.info('{0}'.format('=' * 20))
                logging.info('EPOCH {0}'.format(epoch))

                index_start = randint(0, len(df)-1)
                df_inner = df.iloc[index_start:]
                logging.info('Epoch: at {0} with {1} ticks'.format(index_start, len(df_inner)))
                q, r, error, tick = train(df_inner, q, alpha, epsilon, PERIODS, actions, pip_mul)

                # results
                rewards.append(r)
                errors.append(error * pip_mul)
                ticks.append(tick)

                # prune lengths
                while len(rewards) > 1000 + minutes * 1000:
                    rewards.pop(0)
                    errors.pop(0)
                    ticks.pop(0)

                # RMSD
                rmsd = np.sqrt(np.mean([e**2 for e in errors]))
                logging.info('RMSD: {0}'.format(rmsd))

                # win ratio
                wins = [1. if r > 0. else 0. for r in rewards]

                # adjust values
                # alpha = inverse_val / 4.
                # epsilon = alpha / 3.

                if time() - time_start > time_interval or debug:
                    logging.warn('{0} [{1:05d}] RMSD {2:03d} PPT {3:03d} WR {5:.0f}% [ticks:{6:.1f} sum:{4:.1f}]'.format(
                        currency,
                        epoch,
                        int(rmsd),
                        int(np.mean(rewards) * pip_mul),
                        sum(rewards),
                        np.mean(wins) * 100,
                        np.mean(ticks),
                    ))
                    saveQ(currency, interval, q)
                    time_interval += seconds_info_intervals

                if (time() - time_start >= seconds_to_run) or debug:
                    break

            saveQ(currency, interval, q)

            summarizeActions(q)

            if debug:
                break  # currencies

        if debug:
            break  # forever

        # copyBatch()


########################################################################################################
# SARSA
########################################################################################################

def train(df, q, alpha, epsilon, periods, actions, pip_mul):
    logging.info('Training: started...')
    d = None

    # initial state
    s = getState(df, periods)

    # initial action
    a = getAction(q, s, epsilon, actions)

    # get reward
    r, ticks = getReward(df, a, pip_mul)

    # get delta
    d = getDelta(q, s, a, r)

    # update Q
    q = updateQ(q, s, a, d, r, alpha)

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
    q_sa = q.get(sa, 0)
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