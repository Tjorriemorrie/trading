from google.appengine.ext import ndb
import logging as log
import math


CURRENCIES = ['RDBULL', 'RDBEAR']

TRADE_BASES = ['payout', 'directional']

TRADE_AIMS = ['higher', 'lower']


class Q(ndb.Model):
    data = ndb.PickleProperty(compressed=False)
    visits = ndb.PickleProperty(compressed=False)
    updated_at = ndb.DateTimeProperty(auto_now=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)


class Run(ndb.Model):
    currency = ndb.StringProperty(required=True)
    trade_base = ndb.StringProperty(required=True)
    trade_aim = ndb.StringProperty(required=True)

    ended_at = ndb.DateTimeProperty(required=True)
    # to retrieve runs which needs to get result
    is_finished = ndb.BooleanProperty(default=False)
    # for easy analysis
    is_win = ndb.BooleanProperty()
    # is martingale run completed (not specified by win anymore due to anti-M)
    is_completed = ndb.BooleanProperty(default=False)

    step = ndb.IntegerProperty(default=1)
    binary_ref = ndb.StringProperty(required=True)
    parent_run = ndb.KeyProperty(kind='Run')

    payout = ndb.FloatProperty(required=True, default=2.)
    probability = ndb.FloatProperty(required=True)
    balance = ndb.FloatProperty(default=0.)

    stake = ndb.FloatProperty(required=True)
    stake_parent = ndb.FloatProperty(default=0.)
    stake_net = ndb.FloatProperty()

    profit = ndb.FloatProperty()
    profit_req = ndb.FloatProperty(required=True)
    profit_req_parent = ndb.FloatProperty(default=0.)
    profit_parent = ndb.FloatProperty(default=0.)
    profit_net = ndb.FloatProperty()

    updated_at = ndb.DateTimeProperty(auto_now=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)

    def updateResult(self, profit):
        # parent_stake = run.stake_parent if run.stake_parent else 0.
        self.profit = profit
        self.profit_net = self.profit + self.profit_parent
        self.stake_net = self.stake + self.stake_parent
        self.is_finished = True
        self.is_win = True if self.profit > 0 else False
        self.is_completed = True if self.profit_net > 0 else False
        log.info('Run result: completed {0} with net profit of {1:.2f}'.format(self.is_completed, self.profit_net))

    def setProfitRequired(self, profit_target=1.):
        log.info('Profit req: target = {0}'.format(profit_target))
        profit_req = profit_target
        # modify profit req to handle losses
        if self.step > 1:
            log.info('Profit req: step {0} with running net of {1:.2f}'.format(self.step, self.profit_parent))
            profit_req += abs(self.profit_parent)
            iterations_req = max(1., round(math.log(profit_req / profit_target), 0))
            log.info('Profit req: {0:.0f} iterations req for profit req of {1:.2f}'.format(iterations_req, profit_req))
            profit_req = max(profit_target, profit_req / iterations_req)
        self.profit_req = round(profit_req, 2)
        log.info('Profit req: final {0:.2f}'.format(self.profit_req))

    def getRoi(self):
        '''
        pre
        I 13:45:04.115 S q:-0.184 + e0.003 = v-0.182 for sRDBULL_payout_higher
        I 13:45:04.115 S q:-0.207 + e0.006 = v-0.201 for sRDBULL_payout_lower
        I 13:45:04.115 S q:-0.205 + e0.004 = v-0.201 for sRDBULL_directional_higher
        I 13:45:04.116 S q:-0.188 + e0.005 = v-0.183 for sRDBULL_directional_lower
        I 13:45:04.116 S q:-0.219 + e0.011 = v-0.209 for sRDBEAR_payout_higher
        I 13:45:04.116 S q:-0.235 + e0.009 = v-0.226 for sRDBEAR_payout_lower
        I 13:45:04.116 S q:-0.215 + e0.005 = v-0.211 for sRDBEAR_directional_higher
        I 13:45:04.116 S q:-0.105 + e0.003 = v-0.102 for sRDBEAR_directional_lower
        post
        I 09:00:00.878 S q:-0.219 + e0.019 = v-0.200 for sRDBULL_payout_higher
        I 09:00:00.878 S q:-0.207 + e0.060 = v-0.147 for sRDBULL_payout_lower
        I 09:00:00.878 S q:-0.205 + e0.036 = v-0.169 for sRDBULL_directional_higher
        I 09:00:00.878 S q:-0.188 + e0.047 = v-0.141 for sRDBULL_directional_lower
        I 09:00:00.878 S q:-0.219 + e0.106 = v-0.113 for sRDBEAR_payout_higher
        I 09:00:00.878 S q:-0.235 + e0.085 = v-0.150 for sRDBEAR_payout_lower
        I 09:00:00.878 S q:-0.038 + e0.033 = v-0.005 for sRDBEAR_directional_higher
        I 09:00:00.879 S q:-0.230 + e0.017 = v-0.213 for sRDBEAR_directional_lower
        '''
        return self.profit / self.stake

    def getState(self):
        return '_'.join([self.currency, self.trade_base, self.trade_aim])