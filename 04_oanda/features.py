# open orders
# includes limits, stop losses, take profits and trailing stops
# support and resistance levels
# orders below price means market is bullish
# orders above price means market is bearish
# ol = long orders
# os = short orders

# open positions
# all open long and short positions
# current market sentiment
# ps = short positions
# pl = long positions

# positions:
# in the money
# - short above price
# - long below price
# out of the money
# - short below price
# - long above price

# $ curl -o response.json "https://api-fxpractice.oanda.com/labs/v1/orderbook_data?instrument=EUR_USD&period=3600" -H "Authorization: Bearer e784eb5916aff0cef1e40384f91efcbc-894f13baacee725fe3294136ac8fa469"

from collections import OrderedDict
import numpy as np


def getNames():
    names = []

    # 8
    # sum quadrants
    names.append('orders_longs_above')
    names.append('orders_shorts_above')
    names.append('positions_longs_above')
    names.append('positions_shorts_above')
    names.append('orders_longs_below')
    names.append('orders_shorts_below')
    names.append('positions_longs_below')
    names.append('positions_shorts_below')

    return names


def extractFeatures(data):
    features = []

    # order timestamps
    data = OrderedDict(sorted(data.items()))

    for timestamp, data in data.iteritems():
        if type(data) is int:
            raise Exception('Invalid file')
        tmp = [0] * 8
        rate_current = data['rate']

        # sum quadrants
        for rate_point, percs in data['price_points'].iteritems():
            if float(rate_point) > rate_current:
                tmp[0] += percs['ol']
                tmp[1] += percs['os']
                tmp[2] += percs['pl']
                tmp[3] += percs['ps']
            else:
                tmp[4] += percs['ol']
                tmp[5] += percs['os']
                tmp[6] += percs['pl']
                tmp[7] += percs['ps']

        # add timestamp point to features
        features.append(tmp)

    return features

'''
u'1411548001': {
   'rate': 1.2853,
   'sums': {
        'positions': {
            'longs': {'below': 4.757999999999999, 'above': 51.35969999999999},
            'shorts': {'below': 19.2438, 'above': 24.639399999999995}
        },
        'orders': {
            'longs': {'below': 15.541600000000006, 'above': 16.711199999999995},
            'shorts': {'below': 11.835200000000002, 'above': 55.6986}
        }
   }
},
'''



def calcRewards(data):
    results = []
    iMax = 5 * 1
    rates = [v['rate'] for v in data.values()]
    # print rates
    for pos, rate in enumerate(rates):
        tmp = [0]
        for i in xrange(1, iMax):
            index = pos + i
            if index >= len(rates) - 2:
                break
            tmp.append(rates[index] - rate)
        results.append(sum(tmp))
    mean = np.mean([abs(r) for r in results])
    print 'mean', round(mean, 4)
    mean /= 1.25
    # print 'halve-mean', round(mean, 4)
    rewards = ['long' if abs(r) > mean and r > 0 else 'short' if abs(r) > mean and r < 0 else 'none' for r in results]
    return rewards


def getSplit(features, rewards, split=0.70):
    # sk.cross_validation.train_test_split(
    #     features,
    #     rewards,
    #     test_size=0.30,
    #     random_state=0,
    # )
    size = len(features)
    cutOff = int(size * split)
    X_train = features[:cutOff]
    X_test = features[cutOff:]
    Y_train = rewards[:cutOff]
    Y_test = rewards[cutOff:]
    return X_train, X_test, Y_train, Y_test
