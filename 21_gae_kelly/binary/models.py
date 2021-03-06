from google.appengine.ext import ndb


CURRENCIES = ['EURUSD']

TIME_FRAMES = ['5', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55', '60']
# TIME_FRAMES = ['1']

TRADE_BASES = ['payout', 'directional']

TRADE_AIMS = ['higher', 'lower']


class Q(ndb.Model):
    data = ndb.PickleProperty(compressed=False)
    visits = ndb.PickleProperty(compressed=False)
    updated_at = ndb.DateTimeProperty(auto_now=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)


class Run(ndb.Model):
    currency = ndb.StringProperty()
    time_frame = ndb.StringProperty()
    trade_base = ndb.StringProperty()
    trade_aim = ndb.StringProperty()

    is_finished = ndb.BooleanProperty(default=False)
    is_win = ndb.BooleanProperty()

    binary_ref = ndb.StringProperty()
    parent_run = ndb.KeyProperty(kind='Run')

    step = ndb.IntegerProperty()
    payout = ndb.FloatProperty()
    probability = ndb.FloatProperty()

    stake = ndb.FloatProperty()
    stake_parent = ndb.FloatProperty(default=0.)
    stake_net = ndb.FloatProperty()

    profit = ndb.FloatProperty()
    profit_parent = ndb.FloatProperty(default=0.)
    profit_net = ndb.FloatProperty()

    ended_at = ndb.DateTimeProperty()
    updated_at = ndb.DateTimeProperty(auto_now=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)

    def getState(self):
        return '_'.join([self.currency, self.time_frame, self.trade_base, self.trade_aim])