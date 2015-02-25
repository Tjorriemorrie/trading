import logging
import os
from os.path import realpath, dirname, join, isfile
from os import listdir
import pandas as pd
import numpy as np
import pickle
import argparse
from random import random, choice, shuffle
from pprint import pprint
from sklearn.preprocessing import scale
from time import time, sleep
import operator
import datetime
import calendar
import shutil
import tempfile


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


def main(debug):
    interval = choice(INTERVALS)

    minutes = 0
    while True:
        minutes += 1
        seconds_to_run = 60 * minutes
        seconds_info_intervals = seconds_to_run / 3
        logging.error('Training each currency for {0} minutes'.format(minutes))

        shuffle(CURRENCIES)
        for currency in CURRENCIES:

            df = loadData(currency, interval)

            df = dropOutliers(df)

            df = setGlobalStats(df)
            # print df

            alpha = 0.
            epsilon = 0.
            gamma = 0.9
            lamda = 0.
            q = loadQ(currency, interval)

            group_data = getGroupOptimus(df)
            time_start = time()
            time_interval = 0

            epoch = 0
            results = []
            etraces = {}
            # train till accuracy is reached
            logging.warn('Training {0} on {1} with {2} groups...'.format(currency, interval, len(group_data)))
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
                    bdays = group_info['bdays']
                    q, r, trail, etraces = train(group_df, q, alpha, epsilon, gamma, optimus, lamda, etraces, bdays)
                    # logging.error('{2:.2f} trail vs optimus = {0} vs {1}'.format(trail, optimus, r))
                    results.append(r)
                    if debug:
                        break  # df groups

                # results
                results_avg = np.mean(results)
                results_std = np.std(results)
                while len(results) > minutes * 1000:
                    # results.remove(min(results[:int(len(results)*results_avg)]))
                    results.pop(0)

                # adjust values
                inverse_val = 1. - max(results_avg, 0.001)
                lamda = max(results_avg, 0)
                alpha = inverse_val / 4.
                epsilon = alpha / 3.

                if time() - time_start > time_interval or debug:
                    logging.warn('{7} [{0}] {1:.0f}/{6:.0f}/{5:.0f} % [e:{2:.2f}% a:{3:.1f}% l:{4:.0f}%]'.format(
                        epoch,
                        (results_avg - results_std) * 100,
                        epsilon * 100,
                        alpha * 100,
                        lamda * 100,
                        (results_avg + results_std) * 100,
                        results_avg * 100,
                        currency,
                    ))
                    saveQ(currency, interval, q)
                    time_interval += seconds_info_intervals

                if (len(results) > 100 and time() - time_start >= seconds_to_run) or debug:
                    # logging.error('{1} training finished at upper {0:.0f}%'.format((results_avg + results_std) * 100, currency))
                    break

            saveQ(currency, interval, q)

            if debug:
                break  # currencies

        if debug:
            break  # forever

        copyBatch()


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


def setGlobalStats(df):
    logging.info('DF: adding non-state stats...')

    # moving average
    hlc = df.apply(lambda x: (x['high'] + x['low'] + x['close']) / 3, axis=1)

    avg_5 = pd.rolling_mean(hlc, 5)
    avg_5_y = avg_5.shift(+1)
    df['ma_quick_bullish'] = avg_5 >= avg_5_y
    avg_5_diff = abs(avg_5 - avg_5_y)
    avg_5_diff_y = avg_5_diff.shift(+1)
    df['ma_quick_divergence'] = avg_5_diff >= avg_5_diff_y
    df['ma_quick_magnitude'] = avg_5_diff > avg_5_diff.mean()

    avg_20 = pd.rolling_mean(hlc, 20)
    avg_20_y = avg_20.shift(+1)
    df['ma_signal_bullish'] = avg_20 >= avg_20_y
    avg_20_diff = abs(avg_20 - avg_20_y)
    avg_20_diff_y = avg_20_diff.shift(+1)
    df['ma_signal_divergence'] = avg_20_diff >= avg_20_diff_y
    df['ma_signal_magnitude'] = avg_20_diff > avg_20_diff.mean()

    df['ma_crossover_bullish'] = avg_5 >= avg_20
    ma_diff = avg_5 - avg_20
    ma_diff_y = avg_5_y - avg_20_y
    df['ma_crossover_divergence'] = ma_diff >= ma_diff_y
    df['ma_crossover_magnitude'] = ma_diff >= ma_diff.mean()

    # pivots
    df_pivots = pd.DataFrame(dtype=float)
    df_pivots['hlc'] = hlc
    df_pivots['hlc_y1'] = hlc.shift(1)
    df_pivots['hlc_y2'] = hlc.shift(2)
    df_pivots['hlc_y3'] = hlc.shift(3)
    df_pivots['hlc_y4'] = hlc.shift(4)
    df['pivot_high_major'] = df_pivots.apply(lambda x: 1 if (x['hlc_y4'] < x['hlc_y3'] < x['hlc_y2'] and x['hlc_y2'] > x['hlc_y1'] > x['hlc']) else 0, axis=1)
    df['pivot_high_minor'] = df_pivots.apply(lambda x: 1 if (x['hlc_y2'] < x['hlc_y1'] and x['hlc_y1'] > x['hlc']) else 0, axis=1)
    df['pivot_low_major'] = df_pivots.apply(lambda x: 1 if (x['hlc_y4'] > x['hlc_y3'] > x['hlc_y2'] and x['hlc_y2'] < x['hlc_y1'] < x['hlc']) else 0, axis=1)
    df['pivot_low_minor'] = df_pivots.apply(lambda x: 1 if (x['hlc_y2'] > x['hlc_y1'] and x['hlc_y1'] < x['hlc']) else 0, axis=1)

    # situationals
    df['higher_high'] = df_pivots.apply(lambda x: 1 if (x['hlc'] > x['hlc_y1']) else 0, axis=1)
    df['lower_low'] = df_pivots.apply(lambda x: 1 if (x['hlc'] < x['hlc_y1']) else 0, axis=1)
    df['higher_soldiers'] = df_pivots.apply(lambda x: 1 if (x['hlc'] > x['hlc_y1'] > x['hlc_y2']) else 0, axis=1)
    df['lower_soldiers'] = df_pivots.apply(lambda x: 1 if (x['hlc'] < x['hlc_y1'] < x['hlc_y2']) else 0, axis=1)

    # ATR
    df_atr = pd.DataFrame(dtype=float)
    df_atr['range'] = df['range']
    df_atr['close_y'] = df['close'].shift(+1)
    df_atr['h_from_c'] = abs(df['high'] - df_atr['close_y'])
    df_atr['l_from_c'] = abs(df['low'] - df_atr['close_y'])
    df_atr['tr'] = df_atr.apply(lambda x: max(x['range'], x['h_from_c'], x['l_from_c']), axis=1)

    avg_5 = pd.rolling_mean(df_atr['tr'], 5)
    avg_5_y = avg_5.shift(+1)
    df['atr_quick_bullish'] = avg_5 >= avg_5_y
    avg_5_diff = abs(avg_5 - avg_5_y)
    avg_5_diff_y = avg_5_diff.shift(+1)
    df['atr_quick_divergence'] = avg_5_diff >= avg_5_diff_y
    df['atr_quick_magnitude'] = avg_5_diff > avg_5_diff.mean()

    avg_20 = pd.rolling_mean(df_atr['tr'], 20)
    avg_20_y = avg_20.shift(+1)
    df['atr_signal_bullish'] = avg_20 >= avg_20_y
    avg_20_diff = abs(avg_20 - avg_20_y)
    avg_20_diff_y = avg_20_diff.shift(+1)
    df['atr_signal_divergence'] = avg_20_diff >= avg_20_diff_y
    df['atr_signal_magnitude'] = avg_20_diff > avg_20_diff.mean()

    df['atr_crossover_bullish'] = avg_5 >= avg_20
    atr_diff = avg_5 - avg_20
    atr_diff_y = avg_5_y - avg_20_y
    df['atr_crossover_divergence'] = atr_diff >= atr_diff_y
    df['atr_crossover_magnitude'] = atr_diff >= atr_diff.mean()

    # print df
    # raise Exception('foo')

    logging.info('DF: added non-state stats')
    return df


def loadQ(currency, interval):
    logging.info('Q: loading...')
    try:
        with open('{0}/models/{1}_{2}.q'.format(realpath(dirname(__file__)), currency, interval), 'rb') as f:
            q = pickle.load(f)
    except (IOError, EOFError) as e:
        logging.error('Could not load Q for {0}'.format(currency))
        q = {}
    logging.info('Q: loaded {0}'.format(len(q)))
    return q


def saveQ(currency, interval, q):
    logging.info('Q: saving...')
    filename = '{0}/models/{1}_{2}.q'.format(realpath(dirname(__file__)), currency, interval)
    with tempfile.NamedTemporaryFile('wb', dir=os.path.dirname(filename), delete=False) as tf:
        pickle.dump(q, tf)
        tempname = tf.name
        os.rename(tempname, filename)
    logging.info('Q: saved {0}'.format(len(q)))


def train(df, q, alpha, epsilon, gamma, optimus, lamda, etraces, bdays):
    logging.info('Training: started...')
    r = 0.
    trail = ''

    # initial state
    i = 0.
    s = getState(df, i, bdays)

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
            s_next = getState(df, i_next, bdays, s_ts)
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

        if not len(group_df):
            logging.info('Skipping {0} as no days'.format(group_name))
            continue

        first_bday = group_df.index[0]
        first_day = first_bday.replace(day=1)
        last_day = first_day.replace(day=calendar.monthrange(first_bday.year, first_bday.month)[1])
        bdays = pd.bdate_range(start=first_bday, end=last_day)

        if len(group_df) / len(bdays) < 0.50:
            logging.info('Skipping {0} as not enough days'.format(group_name))
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
            'bdays': len(bdays),
        }

    logging.info('Group Optimus: calculated {0}'.format(len(group_data)))
    return group_data


def copyBatch():
    src = '{0}/models'.format(realpath(dirname(__file__)))
    dest = '{0}/batch'.format(realpath(dirname(__file__)))
    src_files = listdir(src)
    for file_name in src_files:
        full_file_name = join(src, file_name)
        if isfile(full_file_name):
            shutil.copy(full_file_name, dest)


########################################################################################################
# WORLD
########################################################################################################

def getState(df, i, bdays, s_ts=None):
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
    s_group_progress = [1 if (i+1)/bdays > t/25. else 0 for t in xrange(0, 25)]
    s += s_group_progress
    logging.debug('State: group progress {0}'.format(s_group_progress))

    # current row
    row = df.iloc[i]
    # print row

    # trend 5/20
    s_trend = []
    s_trend.append(1 if row['ma_quick_bullish'] else 0)
    s_trend.append(1 if row['ma_quick_divergence'] else 0)
    s_trend.append(1 if row['ma_quick_magnitude'] else 0)
    s_trend.append(1 if row['ma_signal_bullish'] else 0)
    s_trend.append(1 if row['ma_signal_divergence'] else 0)
    s_trend.append(1 if row['ma_signal_magnitude'] else 0)
    s_trend.append(1 if row['ma_crossover_bullish'] else 0)
    s_trend.append(1 if row['ma_crossover_divergence'] else 0)
    s_trend.append(1 if row['ma_crossover_magnitude'] else 0)
    s += s_trend
    logging.debug('State: moving average {0}'.format(s_trend))

    # peaks
    s_peaks = [
        row['pivot_high_major'],
        row['pivot_high_minor'],
        row['pivot_low_major'],
        row['pivot_low_minor']
    ]
    s += s_peaks
    logging.debug('State: peaks {0}'.format(s_peaks))

    # situationals
    s_situationals = [
        row['higher_high'],
        row['lower_low'],
        row['higher_soldiers'],
        row['lower_soldiers']
    ]
    s += s_situationals
    logging.debug('State: situationals {0}'.format(s_situationals))

    # ATR 5/20
    s_atr = []
    s_atr.append(1 if row['atr_quick_bullish'] else 0)
    s_atr.append(1 if row['atr_quick_divergence'] else 0)
    s_atr.append(1 if row['atr_quick_magnitude'] else 0)
    s_atr.append(1 if row['atr_signal_bullish'] else 0)
    s_atr.append(1 if row['atr_signal_divergence'] else 0)
    s_atr.append(1 if row['atr_signal_magnitude'] else 0)
    s_atr.append(1 if row['atr_crossover_bullish'] else 0)
    s_atr.append(1 if row['atr_crossover_divergence'] else 0)
    s_atr.append(1 if row['atr_crossover_magnitude'] else 0)
    s += s_atr
    logging.debug('State: average true range {0}'.format(s_atr))

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
    logging.info('Reward: trail vs optimus [{0} vs {1}]'.format(trail, optimus))
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

    # penalties
    # if trade does not eom
    if len(optimus) == len(trail) and trail[-1] != '!':
        r -= 1.00
        logging.debug('Trail does not end at end of group {0}'.format(trail))
    # if trade length is too small
    r_length = 1. / (trail.count('S') + trail.count('B') + 1.)
    r -= r_length
    logging.debug('Trail length penalised with {0}'.format(r_length))

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
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    debug = args.debug
    lvl = logging.DEBUG if debug else logging.WARN

    logging.basicConfig(
        level=lvl,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main(debug)