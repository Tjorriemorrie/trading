import logging
from os.path import realpath, dirname
import pandas as pd
import numpy as np
import pickle
from random import random, choice
from pprint import pprint
from sklearn.preprocessing import scale
from time import sleep


CURRENCIES = [
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

INTERVALS = [
    # '60',
    '1440',
]

ACTIONS = [
    'waiting',
    'enter-long',
    'stay-long',
    'exit-long',
    'enter-short',
    'stay-short',
    'exit-short',
    'completed',
]



def main():
    interval = choice(INTERVALS)
    for currency in CURRENCIES:
        logging.info('Training {0} on {1}...'.format(currency, interval))

        df = loadData(currency, interval)

        df = dropOutliers(df)

        # df = setGlobalStats(df)

        alpha = 0.10
        epsilon = 0.10
        gamma = 0.90
        q = loadQ(currency, interval)

        for group_name, group_df in df.groupby(pd.TimeGrouper(freq='M')):
            group_max = group_df.close.max()
            group_min = group_df.close.min()
            reward_max = group_max - group_min
            logging.info('Max reward for set {0:.4f} (max {1:.4f} min {2:.4f})'.format(reward_max, group_max, group_min))
            optimus = ''
            state = '_'
            for i, row in group_df[:-1].iterrows():
                # enter buy?
                if row['close'] == group_min:
                    state = 'B' if state == '_' else '!'
                # enter sell?
                if row['close'] == group_max:
                    state = 'S' if state == '_' else '!'
                optimus += state
                if state == '!':
                    break
            logging.error('{0} {1}'.format(len(optimus), ''.join(optimus)))
            sleep(5)

            epoch = 0
            results = []
            while True:
                epoch += 1
                logging.info(' ')
                logging.info('{0}'.format('=' * 20))
                logging.info('EPOCH {0}'.format(epoch))
                q, r = train(group_df, q, alpha, epsilon, gamma, optimus)

                results.append(r)
                while len(results) > 1000:
                    results.pop(0)
                logging.warn('{0} terminated: progress {1:.0f}%'.format(epoch, sum(results) / len(results) * 100))

                # sleep(0.1)
                break  # epochs

                # save periodically
                if epoch % 500 == 0:
                    saveQ(currency, interval, q)

            break  # groups

        saveQ(currency, interval, q)

        break  # currencies


def loadData(currency, interval):
    logging.info('Data: loading {0} at {1}...'.format(currency, interval))
    df = pd.read_csv(
        r'{0}/../data/{1}{2}.csv'.format(realpath(dirname(__file__)), currency, interval),
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        parse_dates=[[0, 1]],
        index_col=0,
    ).astype(float)
    logging.info('Data: {0} rows loaded'.format(len(df)))
    return df


def dropOutliers(df):
    logging.info('Outliers: dropping...')
    size_start = len(df)

    # get range
    df['range'] = df.high - df.low
    # print df

    # get stats
    mean = df.range.mean()
    std = df.range.std()

    # drop outliers
    min_cutoff = mean - std * 2
    max_cutoff = mean + std * 2
    logging.debug('Dropping outliers between below {0:4f} and above {1:4f}'.format(min_cutoff, max_cutoff))
    df = df[df.range > min_cutoff]
    df = df[df.range < max_cutoff]
    logging.debug('Dropped {0} rows'.format(500 - len(df)))

    logging.info('Outliers: {0} removed'.format(size_start - len(df)))
    return df


def loadQ(currency, interval):
    logging.info('Q: loading...')
    try:
        with open('{0}/models/{1}_{2}.q'.format(realpath(dirname(__file__)), currency, interval), 'r') as f:
            q = pickle.load(f)
    except IOError:
        q = {}
    logging.info('Q: loaded {0}'.format(len(q)))
    return q


def saveQ(currency, interval, q):
    logging.info('Q: saving...')
    with open('{0}/models/{1}_{2}.q'.format(realpath(dirname(__file__)), currency, interval), 'w') as f:
        pickle.dump(q, f)
    logging.error('Q: saved {0}'.format(len(q)))


def train(df, q, alpha, epsilon, gamma, optimus):
    logging.info('Training: started...')
    r = 0.
    trail = ''

    # initial state
    i = 0.
    s = getState(df, i)
    close_entry = None

    # initial action
    a = getAction(q, s, epsilon)

    for date_time, row in df[:-1].iterrows():
        logging.info(' ')
        logging.info('Environment: {0}/{1} {2}'.format(i, len(df)-1, date_time))

        logging.info('State: {0}'.format(sum(s)))
        logging.info('Action: {0}'.format(a))

        # take action (get trade status for s_next)
        s_ts, trail = takeAction(s, a, trail)

        # save entry
        r = getReward(trail, optimus)

        # next environment
        i_next = i + 1
        s_next = getState(df, i_next, s_ts)
        a_next = getAction(q, s_next, epsilon)

        # update Q
        q = updateQ(q, s, a, r, s_next, a_next, gamma, alpha)

        # until s is terminal
        if s_ts[3]:
            trail.append('!')
            break
        else:
            trail.append('_' if a in ['waiting', 'completed'] else ('B' if a in ['enter-long', 'stay-long'] else 'S'))

        a = a_next
        s = s_next
        i += 1

    logging.warn('Training: ended {0} => {1:.2f}'.format(''.join(trail), r))
    return q, r



########################################################################################################
# WORLD
########################################################################################################

def getState(df, i, s_ts=None):
    logging.info('State: from {0}...'.format(i))
    s = []

    # trade status
    if not s_ts:
        s_trade_status = [1, 0, 0, 0]
    else:
        s_trade_status = s_ts
    s += s_trade_status
    logging.debug('State: trade status {0}'.format(s_trade_status))

    # group progress
    s_group_progress = [1 if i/len(df) > t/100. else 0 for t in xrange(0, 100)]
    s += s_group_progress
    logging.debug('State: group progress {0}'.format(s_group_progress))

    logging.info('State: {0}/{1}'.format(sum(s), len(s)))
    return s


def getActionsAvailable(trade_status):
    logging.debug('Action: finding available for {0}...'.format(trade_status))

    # validate trade status
    if sum(trade_status) != 1:
        raise Exception('Invalid trade status')

    # looking
    if trade_status[0]:
        actions_available = ['waiting', 'enter-long', 'enter-short']
    # buying
    elif trade_status[1]:
        actions_available = ['stay-long', 'exit-long']
    # selling
    elif trade_status[2]:
        actions_available = ['stay-short', 'exit-short']
    # finished
    elif trade_status[3]:
        actions_available = ['completed']
    else:
        raise Exception('Unknown state {0}'.format(trade_status))

    logging.debug('Action: found {0} for {1}...'.format(actions_available, trade_status))
    return actions_available


def takeAction(s, a, trail):
    logging.info('Change: state {0} with action {1}...'.format(s, a))

    # take action
    if a in ['waiting']:
        s_trade_status = [1, 0, 0, 0]
        trail += '_'
    elif a in ['enter-long', 'stay-long']:
        s_trade_status = [0, 1, 0, 0]
        trail += 'B'
    elif a in ['enter-short', 'stay-short']:
        s_trade_status = [0, 0, 1, 0]
        trail += 'S'
    elif a in ['exit-long', 'exit-short', 'completed']:
        s_trade_status = [0, 0, 0, 1]
        trail += '!'
    else:
        raise Exception('Unknown action [{0}] to take on state [{1}]'.format(a, s[:4]))

    logging.info('Change: trail = {0}'.format(trail))
    logging.info('Change: state is now {0}...'.format(s_trade_status))
    return s_trade_status


def getReward(a, close_now, close_entry, reward_max, progress):
    logging.info('Reward: getting at progress {0}...'.format(progress))
    # take profits from exits
    if a == 'exit-long':
        r = close_now - close_entry
        # r = (close_now - close_entry) - (reward_max / 2)
        # r -= (reward_max - r) * (1 - progress)
    elif a == 'exit-short':
        r = close_entry - close_now
        # r = (close_entry - close_now) - (reward_max / 2)
        # r -= (reward_max - r) * (1 - progress)
    # penalty if no trading
    elif progress == 1:
        r = -reward_max
    # progress penalised reward
    else:
        r = 0
    logging.debug('Reward: raw {0}'.format(r))
    # enhance growth
    # r -= reward_max
    # logging.debug('Reward: deduced {0}'.format(r))
    # scale reward
    r /= reward_max
    logging.info('Reward: scaled {0:.4f}'.format(r))
    return r



########################################################################################################
# SARSA
########################################################################################################

def getAction(q, s, epsilon):
    logging.info('Action: finding...')

    actions_available = getActionsAvailable(s[:4])

    # exploration
    if random() < epsilon:
        logging.debug('Action: explore ({0:.2f})'.format(epsilon))
        a = choice(actions_available)

    # exploitation
    else:
        logging.debug('Action: exploit ({0:.2f})'.format(epsilon))
        q_max = None
        for action in actions_available:
            q_sa = q.get((tuple(s), action), random() * 10)
            logging.debug('Qsa {0} {1:.2f}'.format(action, q_sa))
            if q_sa > q_max:
                q_max = q_sa
                a = action

    logging.info('Action: found {0}'.format(a))
    return a


def updateQ(q, s, a, r, s_next, a_next, gamma, alpha):

    q_sa = q.get((tuple(s), a), -r)
    q_sa_next = q.get((tuple(s_next), a_next), -r)
    d = r + (gamma * q_sa_next) - q_sa
    if d:
        logging.debug('Q: Qsa before {0:.4f}'.format(q_sa))
        logging.debug('Q: Delta: calculated {0:.2f}'.format(d))
        q_sa_updated = q_sa + (alpha * d)
        q[(tuple(s), a)] = q_sa_updated
        logging.debug('Q: Qsa after {0:.4f}'.format(q[(tuple(s), a)]))

    return q


########################################################################################################


if __name__ == '__main__':
    logging.basicConfig(
        # level=logging.WARN,
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )
    main()