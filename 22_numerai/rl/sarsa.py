import gzip
import logging
import operator
import os
import pickle
from world import World

logging.getLogger(__name__)

class Sarsa():

    def __init__(self, filename):
        self.filename = filename
        self.world = World()

        self.alpha = 0.
        self.epsilon = self.alpha / 2.
        self.delta = None


    def __enter__(self):
        try:
            with gzip.open(self.filename) as fz:
                q = pickle.load(fz)
        except (IOError, EOFError) as e:
            logging.warn('Could not load Q at {}'.format(self.filename))
            q = {}
        self.q = q
        logging.debug('Q loaded')

    def __exit__(self, exc_type, exc_value, traceback):
        # filename_tmp = '{0}/models/tmp.pklz'.format(os.path.realpath(os.path.dirname(__file__)))
        # filename = '{0}/models/{1}_{2}.pklz'.format(os.path.realpath(os.path.dirname(__file__)), currency, interval)
        with gzip.open(self.filename, 'wb') as fz:
            pickle.dump(self.q, fz)
            # os.rename(filename_tmp, filename)
        logging.debug('Q saved')

    def train(self):
        logging.info('training...')

        # reset delta
        self.delta = None
    
        # initial state
        s = getState(df, periods)
    
        # initial action
        a = getAction(q, s, epsilon, actions)
    
        # get reward
        r, ticks = getReward(df, a, pip_mul, std)
    
        # get delta
        d = getDelta(q, s, a, r)
    
        # update Q
        q = updateQ(q, s, a, d, r, alpha)
    
        return q, r, d, ticks
    



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
