from google.appengine.ext import ndb


CURRENCIES = ['EURUSD']

TIME_FRAMES = ['5', '10', '15']

TRADE_BASES = ['payout', 'directional']

TRADE_AIMS = ['higher', 'lower']


class Q(ndb.Model):
    data = ndb.PickleProperty(compressed=False)
    updated_at = ndb.DateTimeProperty(auto_now=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)


class Run(ndb.Model):
    currency = ndb.StringProperty(choices=CURRENCIES)
    time_frame = ndb.StringProperty(choices=TIME_FRAMES)
    trade_base = ndb.StringProperty(choices=TRADE_BASES)
    trade_aim = ndb.StringProperty(choices=TRADE_AIMS)

    is_finished = ndb.BooleanProperty(default=False)
    is_win = ndb.BooleanProperty()

    binary_ref = ndb.StringProperty()
    parent_run = ndb.KeyProperty(kind='Run')

    step = ndb.IntegerProperty()
    payout = ndb.FloatProperty()
    stake = ndb.FloatProperty()
    profit = ndb.FloatProperty()
    profit_parent = ndb.FloatProperty(default=0.)
    profit_net = ndb.FloatProperty()

    ended_at = ndb.DateTimeProperty()
    updated_at = ndb.DateTimeProperty(auto_now=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
