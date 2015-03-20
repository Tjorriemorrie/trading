from random import choice
from pprint import pprint


def backtest(df, takeProfit, stopLoss, enterAt, waitFor, factor, cutOff):
    wins = []
    losses = []
    # sample size for testing
    for i in xrange(cutOff):
        # get random start point
        startAt = choice(df.index)
        d = df.ix[startAt]

        # create trade
        trade = {
            'cnt': 0,
            'date': d['date'],
            'close': d['close'],
            'enterAt': d['close'] - enterAt / factor,
            'active': False,
            'outcome': 0,
        }
        # stop levels depends on entry
        trade['takeProfit'] = trade['enterAt'] + takeProfit / factor
        trade['stopLoss'] = trade['enterAt'] - stopLoss / factor
        # p# print(trade)

        # validate trade
        # stop loss
        if trade['stopLoss'] > trade['enterAt']:
            # print 'invalid stop loss'
            break
        # take profit
        if trade['takeProfit'] < trade['enterAt']:
            # print 'invalid take profit'
            break

        # get result
        for k, d in df.iloc[startAt:].iterrows():
            trade['cnt'] += 1

            # check entry for BUY LIMIT
            if not trade['active'] and d['low'] < trade['enterAt']:
                trade['active'] = True
                # print i, d['date'], 'entered', trade['enterAt']

            # check exits
            elif trade['active']:
                # loss?
                if d['low'] < trade['stopLoss']:
                    trade['outcome'] += trade['enterAt'] - trade['stopLoss']
                    # trade['outcome'] += trade['cnt'] / factor
                    trade['outcome'] += 2 / factor
                    losses.append(trade)
                    # print i, d['date'], 'loss', trade['stopLoss']
                    break
                # win?
                elif d['high'] > trade['takeProfit']:
                    trade['outcome'] += trade['takeProfit'] - trade['enterAt']
                    # trade['outcome'] -= trade['cnt'] / factor
                    trade['outcome'] -= 2 / factor
                    wins.append(trade)
                    # print i, d['date'], 'win', trade['takeProfit']
                    break
                else:
                    # # print i, d['date'], 'continue', trade['cnt']
                    pass

            # expire at (cannot wait any longer to enter :(
            elif trade['cnt'] >= waitFor:
                # print i, d['date'], 'outta time'
                break

    return wins, losses