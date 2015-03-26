import logging as log
from models import CURRENCIES, TIME_FRAMES, TRADE_BASES, TRADE_AIMS
import random


class RL():

    def __init__(self):
        self.alpha = 0.10
        log.info('RL alpha = {0:.0f}'.format(self.alpha * 100))


    def selectNew(self, q, epsilon):
        log.info('RL action selecting with epsilon {0}'.format(epsilon))

        # get all possible states
        states = []
        for currency in CURRENCIES:
            for time_frame in TIME_FRAMES:
                for trade_base in TRADE_BASES:
                    for trade_aim in TRADE_AIMS:
                        states.append('_'.join([currency, time_frame, trade_base, trade_aim]))
        log.info('States possible {0}'.format(len(states)))

        # exploration
        if random.random < epsilon:
            state = random.choice(states)
            log.info('State exploration {0}'.format(state))
        # exploitation
        else:
            state = None
            max_val = 0
            for s in states:
                val = q.get(state, random.random() * 10)
                if val > max_val:
                    state = s
                    max_val = val
            log.info('State exploitation {0}'.format(state))

        return state.split('_')


    def updateQ(self, q, run):
        log.info('Q updating...')

        data = q.data
        s = '_'.join([run.currency, run.time_frame, run.trade_base, run.trade_aim])
        r = run.profit_net / run.stake_net

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
        return q