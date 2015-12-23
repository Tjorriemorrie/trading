import logging
import os
import pickle
import operator
import gzip
import pandas as pd
import numpy as np




def loadQ(currency, interval):
    logging.info('Q: loading...')
    try:
        filename = '{0}/models/{1}_{2}.pklz'.format(os.path.realpath(os.path.dirname(__file__)), currency, interval)
        with gzip.open(filename) as fz:
            q = pickle.load(fz)
    except (IOError, EOFError) as e:
        logging.error('Could not load Q for {0}'.format(currency))
        q = {}
    logging.info('Q: loaded {0}'.format(len(q)))
    return q


def saveQ(currency, interval, q):
    logging.info('Q: saving...')
    filename_tmp = '{0}/models/tmp.pklz'.format(os.path.realpath(os.path.dirname(__file__)))
    filename = '{0}/models/{1}_{2}.pklz'.format(os.path.realpath(os.path.dirname(__file__)), currency, interval)
    with gzip.open(filename_tmp, 'wb') as fz:
        pickle.dump(q, fz)
        os.rename(filename_tmp, filename)
    logging.info('Q: saved {0}'.format(len(q)))


def summarizeActions(q):
    summary_total = {}
    summary_count = {}
    for key, value in q.iteritems():
        state, action = key.split('|')
        # total
        action_total = summary_total.get(action, 0)
        action_total += value
        action_total /= 2
        summary_total[action] = action_total

        action_count = summary_count.get(action, 0)
        action_count += 1
        summary_count[action] = action_count

    summary_sorted = sorted(summary_total.items(), key=operator.itemgetter(1))

    for action, info in summary_sorted:
        logging.error('{0:10s} after {2} states with {1:.4f} avg'.format(action, info, summary_count[action]))
