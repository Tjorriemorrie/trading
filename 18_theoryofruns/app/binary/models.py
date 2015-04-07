from google.appengine.ext import ndb
import logging as log
import math


CURRENCIES = ['EURUSD']

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
        self.profit_req = profit_req
        log.info('Profit req: final {0:.2f}'.format(self.profit_req))

    def getRoi(self):
        return self.profit_net / self.stake_net

    def getState(self):
        return '_'.join([self.currency, self.trade_base, self.trade_aim])