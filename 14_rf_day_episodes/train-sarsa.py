import logging
from os.path import realpath, dirname
import pandas as pd
import numpy as np
import pickle
from random import random, choice, shuffle
from pprint import pprint
from sklearn.preprocessing import scale
from time import time, sleep
import operator


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
shuffle(CURRENCIES)

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



def main(debug):
    interval = choice(INTERVALS)
    for currency in CURRENCIES:
        logging.info('Training {0} on {1}...'.format(currency, interval))

        df = loadData(currency, interval)

        df = dropOutliers(df)

        # df = setGlobalStats(df)

        alpha = 0.
        epsilon = 0.
        gamma = 0.9
        lamda = 0.
        q = loadQ(currency, interval)

        group_data = getGroupOptimus(df)
        time_start = time()

        # get accuracy for currency
        for training_step in [0.75, 0.80]:

            epoch = 0
            results = []
            etraces = {}
            # train till accuracy is reached
            while True:
                epoch += 1
                logging.info(' ')
                logging.info('{0}'.format('=' * 20))
                logging.info('EPOCH {0}'.format(epoch))

                # train all groups simultaneously (per epoch) to prevent overfitting
                # go through all groups and then adjust
                for group_name, group_info in group_data.iteritems():
                    logging.info('Training group {0}'.format(group_name))
                    group_df = group_info['group']
                    optimus = group_info['optimus']
                    q, r, trail, etraces = train(group_df, q, alpha, epsilon, gamma, optimus, lamda, etraces)
                    results.append(r)

                # results
                while len(results) > 10000:
                    results.remove(min(results[:int(len(results)*.5)]))
                results_avg = np.mean(results)
                results_std = np.std(results)
                if len(results) > 1000 and results_avg >= training_step:
                    logging.error('Training finished!!!!')
                    break

                    # if debug:
                    #     break  # df groups

                # adjust values
                inverse_val = 1. - max(results_avg, 0.001)
                lamda = inverse_val
                alpha = inverse_val / 3.
                epsilon = alpha / 3.

                if time() - time_start > 120 or debug:
                    # logging.warn('{3} {4:.0f} {5} [{2}] {0} => {1:.0f}%'.format(''.join(trail), r * 100, len(trail), currency, training_step * 100, group_name))
                    logging.warn('{7} {8:.0f} [{0}] {1:.0f}-{6:.0f}-{5:.0f} % [e:{2:.2f}% a:{3:.1f}% l:{4:.0f}%]'.format(
                        epoch,
                        (results_avg - results_std) * 100,
                        epsilon * 100,
                        alpha * 100,
                        lamda * 100,
                        (results_avg + results_std) * 100,
                        results_avg * 100,
                        currency,
                        training_step * 100,
                    ))
                    saveQ(currency, interval, q)
                    time_start = time()

                if debug:
                    break  # epochs

            if debug:
                break  # training steps

        saveQ(currency, interval, q)

        if debug:
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
        with open('{0}/models/{1}_{2}.q'.format(realpath(dirname(__file__)), currency, interval), 'rb') as f:
            q = pickle.load(f)
    except IOError:
        q = {}
    logging.info('Q: loaded {0}'.format(len(q)))
    return q


def saveQ(currency, interval, q):
    logging.info('Q: saving...')
    with open('{0}/models/{1}_{2}.q'.format(realpath(dirname(__file__)), currency, interval), 'wb') as f:
        pickle.dump(q, f)
    logging.info('Q: saved {0}'.format(len(q)))


def train(df, q, alpha, epsilon, gamma, optimus, lamda, etraces):
    logging.info('Training: started...')
    r = 0.
    trail = ''

    # initial state
    i = 0.
    s = getState(df, i)

    # initial action
    a = getAction(q, s, epsilon)

    for date_time, row in df.iterrows():
        logging.info(' ')
        logging.info('Environment: {0}/{1} {2}'.format(i, len(df)-1, date_time))

        logging.info('State: {0}'.format(sum(s)))
        logging.info('Action: {0}'.format(a))

        # take action (get trade status for s_next)
        s_ts, trail = takeAction(s, a, trail)

        # get reward
        r = getReward(trail, optimus)

        # next environment
        i_next = i + 1
        if i_next >= len(df):
            s_next = None
            a_next = None
        else:
            s_next = getState(df, i_next, s_ts)
            a_next = getAction(q, s_next, epsilon)

        # get delta
        d = getDelta(q, s, a, r, s_next, a_next, gamma)

        # update Q
        q, etraces = updateQ(q, s, a, d, r, etraces, lamda, gamma, alpha)

        # until s is terminal
        # we train on whole sequence

        a = a_next
        s = s_next
        i += 1

    return q, r, trail, etraces


def getGroupOptimus(df):
    logging.info('Group Optimus: calculating...')
    group_data = {}
    for group_name, group_df in df.groupby(pd.TimeGrouper(freq='M')):

        if len(group_df) < 18:
            logging.warn('Skipping {0} as not enough days'.format(group_name))
            continue

        group_max = group_df[:-1].close.max()
        group_min = group_df[:-1].close.min()
        reward_max = group_max - group_min
        logging.info('Max reward for set {0:.4f} (max {1:.4f} min {2:.4f})'.format(reward_max, group_max, group_min))

        optimus = ''
        state = '_'
        for i, row in group_df.iterrows():
            # enter buy?
            if row['close'] == group_min:
                state = 'B' if state == '_' else '!'
            # enter sell?
            if row['close'] == group_max:
                state = 'S' if state == '_' else '!'
            optimus += state

        logging.info('[{0}] {1}'.format(len(optimus), ''.join(optimus)))
        group_data[group_name] = {
            'group': group_df,
            'optimus': optimus,
        }

    logging.info('Group Optimus: calculated {0}'.format(len(group_data)))
    return group_data


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
    return s_trade_status, trail


def getReward(trail, optimus):
    logging.info('Reward: trail vs optimus')
    optimus_len = len(optimus) + 0.

    # precision
    r_correct = sum(map(operator.eq, trail, optimus))
    r_precision = r_correct / optimus_len
    logging.debug('Reward: correct {0:.0f} => {1:.2f}'.format(r_correct, r_precision))

    # length
    # r_length_optimus = optimus.count('B' if 'B' in optimus else 'S')
    # r_length_trail = trail.count('B' if 'B' in optimus else 'S')
    # r_length = 1 - (abs(r_length_trail - r_length_optimus) / max(optimus_len - r_length_optimus, r_length_optimus))
    # logging.debug('Reward: trade length {0:.0f} vs {1:.0f} => {2:.2f}'.format(r_length_trail, r_length_optimus, r_length))
    #
    # r = np.mean([r_precision, r_length])
    r = r_precision

    logging.info('Reward: {0:.2f}'.format(r))
    return r



########################################################################################################
# SARSA
########################################################################################################

def getAction(q, s, epsilon):
    logging.info('Action: finding...')

    actions_available = getActionsAvailable(s[:4])

    # exploration
    if random() < epsilon:
        logging.debug('Action: explore (<{0:.2f})'.format(epsilon))
        a = choice(actions_available)

    # exploitation
    else:
        logging.debug('Action: exploit (>{0:.2f})'.format(epsilon))
        q_max = None
        for action in actions_available:
            q_sa = q.get((tuple(s), action), random() * 10.)
            logging.debug('Qsa action {0} is {1:.4f}'.format(action, q_sa))
            if q_sa > q_max:
                q_max = q_sa
                a = action

    logging.info('Action: found {0}'.format(a))
    return a


def getDelta(q, s, a, r, s_next, a_next, gamma):
    logging.info('Delta: calculating...')
    q_sa = q.get((tuple(s), a), 0)
    if not s_next or not a_next:
        q_sa_next = r
    else:
        q_sa_next = q.get((tuple(s_next), a_next), r)
    d = r + (gamma * q_sa_next) - q_sa
    logging.debug('Delta: r [{0:.2f}] + (gamma [{1:.2f}] * Qs`a` [{2:.4f}]) - Qsa [{3:.4f}]'.format(r, gamma, q_sa_next, q_sa))
    logging.info('Delta: {0:.4f}'.format(d))
    return d


def updateQ(q, s, a, d, r, etraces, lamda, gamma, alpha):
    logging.info('Q: updating learning at {0:.2f} with lambda {1:.2f}...'.format(alpha, lamda))

    # update current s,a
    sa = (tuple(s), a)
    etraces[sa] = etraces.get(sa, 0.) + 1

    # update for all etraces
    etraces_updated = {}
    for sa, e_sa in etraces.iteritems():

        # q (only if there is a reward)
        if r:
            q_sa = q.get(sa, r)
            # logging.debug('Q: Qsa before {0:.4f}'.format(q_sa))
            # logging.debug('Q: d:{0:.2f} e:{1:.2f}'.format(d, e_sa))
            q_sa_updated = q_sa + (alpha * d * e_sa)
            q[sa] = q_sa_updated
            logging.debug('Q: before {0:.4f} \t et {1:.2f} \t after {2:.4f}'.format(q_sa, e_sa, q_sa_updated))

        # decay etrace
        if e_sa > 0.01:
            etraces_updated[sa] = e_sa * gamma * lamda

    return q, etraces_updated


########################################################################################################


if __name__ == '__main__':
    debug = False
    lvl = logging.DEBUG if debug else logging.WARN
    logging.basicConfig(
        level=lvl,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )
    main(debug)