import logging
import argparse
import numpy as np
from random import random, choice
from pprint import pprint
from main import loadData, loadQ, getBackgroundKnowledge
from world import DATA, PERIODS, ACTIONS, getState, getReward


def main(debug):
    rmsds = []
    ppts = []
    wrs = []
    for info in DATA:
        currency = info['currency']
        min_trail = info['trail']
        interval = info['intervals'][0]
        pip_mul = info['pip_mul']

        df = loadData(currency, interval, 'test')

        df = getBackgroundKnowledge(df, PERIODS)

        q = loadQ(currency, interval)

        rewards = []
        errors = []
        ticks = []
        for i, row in df.iterrows():
            df_inner = df.loc[i:]
            q, r, error, tick = test(df_inner, q, PERIODS, ACTIONS, pip_mul, info['std'])
            # logging.warn('{0} {1}'.format(i, r))

            # results
            rewards.append(r)
            errors.append(error * pip_mul)
            ticks.append(tick)

        # RMSD
        rmsd = np.sqrt(np.mean([e**2 for e in errors]))

        # win ratio
        wins = [1. if r > 0. else 0. for r in rewards]
        win_ratio = np.mean(wins)

        # ppt
        ppt = np.mean(rewards) * pip_mul

        logging.warn('{0} RMSD {2:03d} PPT {3:03d} WR {5:.0f}% [ticks:{6:.1f} sum:{4:.1f}]'.format(
            currency,
            None,
            int(rmsd),
            int(ppt),
            sum(rewards),
            win_ratio * 100,
            np.mean(ticks),
        ))

        rmsds.append(rmsd)
        ppts.append(ppt)
        wrs.append(win_ratio)

    logging.error('RMSD {0:.0f} +- {1:.0f}'.format(np.mean(rmsds), np.std(rmsds)))
    logging.error('PPT {0:.0f} +- {1:.0f}'.format(np.mean(ppts), np.std(ppts)))
    logging.error('WR {0:.0f} +- {1:.0f}'.format(np.mean(wrs) * 100, np.std(wrs) * 100))


########################################################################################################
# SARSA
########################################################################################################

def test(df, q, periods, actions, pip_mul, std):
    logging.info('Testing: started...')

    # initial state
    s = getState(df, periods)

    # initial action
    a = getAction(q, s, 0, actions)

    # get reward
    r, ticks = getReward(df, a, pip_mul, std)

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
            q_sa = q.get('|'.join([s, action]), random() * 10.)
            logging.debug('Qsa action {0} is {1:.4f}'.format(action, q_sa))
            if q_sa > q_max:
                q_max = q_sa
                a = action

    logging.info('Action: found {0}'.format(a))
    return a


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