import logging as log
from models import CURRENCIES, TRADE_BASES, TRADE_AIMS
import random


class RL():

    def __init__(self):
        self.alpha = 0.01
        log.info('RL alpha = {0:.0f}'.format(self.alpha * 100))
        self.k = 1.
        log.info('RL k = {0:.0f}'.format(self.k))


    def selectNew(self, q):
        log.info('RL action selecting with exploration function of {0}...'.format(self.k))

        # get all possible states
        states = []
        for currency in CURRENCIES:
            for trade_base in TRADE_BASES:
                for trade_aim in TRADE_AIMS:
                    states.append('_'.join([currency, trade_base, trade_aim]))
        log.info('States possible {0}'.format(len(states)))

        state = None
        max_val = 0
        for s in states:
            q_val = q.data.get(s, random.random() * self.k)
            e_val = self.k / float(max(1, q.visits.get(s, 0)))
            val = q_val + e_val
            log.info('S q:{0:.2f} + e{1:.2f} = v{2:.2f} for s{3}'.format(q_val, e_val, val, s))
            if val > max_val:
                state = s
                max_val = val

        log.info('State selected {0}'.format(state))
        return state.split('_')


    def updateQ(self, q, run):
        log.info('Q updating...')

        data = q.data
        s = '_'.join([run.currency, run.trade_base, run.trade_aim])
        r = run.profit_net / run.stake_net
        log.info('Q updating: received {0} reward for state {1}'.format(r, s))

        # get delta
        q_sa = data.get(s, 0.)
        d = r - q_sa
        log.info('Delta: {2:.4f} <= r [{0:.2f}] - Qsa [{1:0.4f}]'.format(r, q_sa, d))

        # q-value
        q_sa_updated = q_sa + (self.alpha * d)
        log.info('Q: {3:.4f} <= qsa [{0:.4f}] + (alpha [{1:.0f}] * d [{2:.4f}])'.format(q_sa, self.alpha * 100, d, q_sa_updated))

        data[s] = q_sa_updated
        log.info('Q updated to {0:.2f}'.format(data[s]))
        q.data = data

        # update visits
        n = q.visits.get(s, 0)
        q.visits[s] = n + 1
        log.info('Q visits updated to {0}'.format(q.visits[s]))

        return q