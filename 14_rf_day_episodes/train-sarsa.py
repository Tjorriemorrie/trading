import logging
from os.path import realpath, dirname
import pandas as pd
import numpy as np
import pickle
from random import random, choice
from pprint import pprint
from sklearn.preprocessing import scale
from sarsa import Sarsa


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
    'stay-out',
    'enter-long',
    'stay-long',
    'exit-long',
    'enter-short',
    'stay-short',
    'exit-short',
]

alpha = 0.50
epsilon = 0.50
gamma = 0.99
thetas = []


def main():
    interval = choice(INTERVALS)
    for currency in CURRENCIES:
        logging.info('Training {0} on {1}...'.format(currency, interval))

        df = loadData(currency, interval)

        df = dropOutliers(df)

        # df = setGlobalStats(df)

        # targets is range

        q = loadQ(currency, interval)

        for group_name, group_df in df.groupby(pd.TimeGrouper(freq='M')):
            train(group_df, q)

            break

        # saveThetas(currency, interval, thetas)

        break


def train(df, q):
    logging.info('Training: started...')
    sarsa = Sarsa(ACTIONS, q)
    epoch = 0

    reward_max = df.high.max() - df.low.min()
    logging.info('Max reward for set {0:.4f}'.format(reward_max))

    while True:
        epoch += 1
        if epoch > 1:
            break
        logging.info(' ')
        logging.info('{0}'.format('=' * 20))
        logging.info('EPOCH {0}'.format(epoch))

        # initial state
        i = 0.
        trade = 'looking'
        s = getState(df, i)
        close_entry = None

        # initial action

        a = getAction(s, trade)

        for date_time, row in df[:-1].iterrows():
            i += 1
            logging.info(' ')
            logging.info('Environment: {0}'.format(date_time))

            logging.info('State: {0}'.format(s))
            logging.info('Action: {0}'.format(a))

            s = takeAction(s, a)
            # save entry
            if a in ['enter-long', 'enter-short']:
                close_entry = row['close']
            r = getReward(a, close_entry, row['close'], reward_max, i >= len(df))

            # next environment
            row_next = df.iloc[i]
            Fsa_next = extractFeatures(df, i)
            a_next = findAction(Fsa_next, s)

            # get delta
            d = calculateDelta(Fsa, a, r, Fsa_next, a_next)

            # update thetas
            updateThetas(d, a)

            a = a_next
            break

        #
        #     # until s is terminal
        #     if aa in [3, 6]:
        #         outcomes.append(closes[s] - closes[iniS] if aa == 3 else closes[iniS] - closes[s])
        #         durations.append(s - iniS)
        #         print '\n', '#', len(outcomes), actions[a], r
        #         print 'Net outcomes', sum(outcomes)
        #         print 'Avg durations', int(sum(durations) / len(durations))
        #         wins = sum([1. for o in outcomes if o > 0])
        #         print currency, 'Win ratio', int(wins / len(outcomes) * 100)
        #         # time.sleep(0.3)
        #
        #     # if iniS not set, then set it
        #     if a == 0 and aa in [1, 4]:
        #         iniS = s
        #
        #     # s <- s'  a <- a'
        #     s = ss
        #     a = aa
        #
        # # save periodically
        # if i % 100 == 99:
        #     saveThetas(currency, interval, thetas)
        #     # print 'Net outcomes', sum(outcomes)
        #     # print currency, 'Win ratio', int(wins / len(outcomes) * 100)
        logging.info('')

    logging.info('Training: ended')
    return thetas


def getState(df, i):
    logging.info('State: from {0}...'.format(i))
    s = []

    # group progress
    s_group_progress = [1 if i/len(df) > t/100. else 0 for t in xrange(0, 100)]
    logging.debug('State: group progress {0}'.format(s_group_progress))
    s += s_group_progress

    logging.info('State: {0} extracted'.format(len(s)))
    return s


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
    # logging.info('Dropping outliers between below {0:4f} and above {1:4f}'.format(min_cutoff, max_cutoff))
    df = df[df.range > min_cutoff]
    df = df[df.range < max_cutoff]
    # logging.info('Dropped {0} rows'.format(500 - len(df)))

    logging.info('Outliers: {0} removed'.format(size_start - len(df)))
    return df


def loadQ(currency, interval):
    logging.info('Q: loading...')
    try:
        with open('{0}/models/{1}_{2}.q'.format(realpath(dirname(__file__)), currency, interval), 'r') as f:
            q = pickle.load(f)
    except IOError:
        q = {}
    logging.debug('Q: {0}'.format(q))
    logging.info('Q: loaded')


def saveThetas(currency, interval, thetas):
    logging.info('Thetas: saving...')
    with open('{0}/models/{1}_{2}.thts'.format(realpath(dirname(__file__)), currency, interval), 'w') as f:
        pickle.dump(thetas, f)
    logging.info('Thetas: saved')


def getReward(a, close_now, close_entry, reward_max, is_last):
    logging.info('Rewards: getting...')
    # take profits from exits
    if a == 'exit-long':
        r = close_now - close_entry
    elif a == 'exit-short':
        r = close_entry - close_now
    # penalty if no trading
    elif is_last:
        r = -reward_max
    # no reward otherwise
    else:
        r = 0
    # scale reward
    r /= reward_max
    logging.info('Rewards: got {0:.2f}'.format(r))
    return r


def getAction(s, trade):
    logging.info('Action: finding...')

    actions_available = getActionsAvailable(trade)

    # exploration
    if random() < epsilon:
        logging.debug('Action: explore ({0:.2f})'.format(epsilon))
        a = choice(actions_available)

    # exploitation
    else:
        logging.debug('Action: exploit ({0:.2f})'.format(epsilon))
        aMax = None
        QsaHighest = -1000
        for a in actions_available:
            Qsa = getActionStateValue(Fsa, a)
            if Qsa > QsaHighest:
                QsaHighest = Qsa
                aMax = a
        a = aMax

    logging.info('Action: found {0}'.format(a))
    return a


def getActionsAvailable(trade):
    logging.debug('Action: finding available for {0}...'.format(trade))

    if trade == 'looking':
        actions_available = ['stay-out', 'enter-long', 'enter-short']
    elif trade == 'bought':
        actions_available = ['stay-long', 'exit-long']
    elif trade == 'sold':
        actions_available = ['stay-short', 'exit-short']
    elif trade == 'finished':
        actions_available = ['stay-out']
    else:
        raise Exception('Unknown state {0}'.format(trade))

    logging.debug('Action: found {0} actions available for {1}...'.format(len(actions_available), trade))
    return actions_available


def getActionStateValue(Fsa, a):
    logging.debug('Qsa: calculating {0}...'.format(a))
    global thetas

    # validate thetas
    if len(thetas) != len(ACTIONS):
        logging.warn('Thetas: invalid!')
        logging.warn('Thetas: re-initializing...')
        thetas = {action: scale([np.random.random(len(Fsa))], axis=1)[0] for action in ACTIONS}
        # logging.debug('Thetas = {0}'.format(thetas))

    # calculate
    Qsa = sum(f * t for f, t in zip(Fsa, thetas[a]))

    logging.debug('Qsa: calculated {0:.2f} for {1}'.format(Qsa, a))
    return float(Qsa)


def takeAction(s, a):
    logging.info('State: taking action {0}...'.format(a))
    # before trade
    if s == 'looking' and a == 'stay-out':
        pass
    # entering buy
    elif s == 'looking' and a == 'enter-long':
        s = 'bought'
    # staying buy
    elif s == 'bought' and a == 'stay-long':
        pass
    # exiting buy
    elif s == 'bought' and a == 'exit-long':
        s = 'finished'
    # entering sell
    elif s == 'looking' and a == 'enter-short':
        s = 'sold'
    # staying sell
    elif s == 'sold' and a == 'stay-short':
        pass
    # exit sell
    elif s == 'sold' and a == 'exit-short':
        s = 'finished'
    # after trade
    elif s == 'finished':
        pass
    else:
        raise Exception('Unknown action [{0}] to take on state [{1}]'.format(a, s))
    logging.info('State is now: {0}'.format(s))
    return s


def calculateDelta(Fsa, a, r, Fsa_next, a_next):
    logging.info('Delta: calculating...')

    Qsa = getActionStateValue(Fsa, a)
    Qsa_next = getActionStateValue(Fsa_next, a_next)
    d = r + (gamma * Qsa_next) - Qsa

    logging.info('Delta: calculated {0:.2f}'.format(d))
    return d


def updateThetas(d, a):
    logging.info('Thetas: updating...')
    global thetas

    thetas_before = thetas[a]
    logging.debug('Thetas before: {0}'.format(thetas[a]))

    # update
    thetas[a] = map(lambda x: x + (alpha * d), thetas[a])
    logging.debug('Thetas adj: {0}'.format(thetas[a]))

    # normalize
    thetas[a] = scale([thetas[a]], axis=1)[0]
    logging.debug('Thetas scaled: {0}'.format(thetas[a]))

    logging.info('Thetas: updated')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )
    main()