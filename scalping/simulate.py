from random import choice


def backtest(df, takeProfit, stopLoss, entry, waitFor, exitAt, factor, cutOff=5000):
    wins = []
    losses = []
    # sample size for testing
    i = 0
    while len(wins) + len(losses) < cutOff:
        i += 1
        # get random start point
        startAt = choice(df.index)
        d = df.ix[startAt]

        # create trade
        trade = {
            'cnt': 0,
            'date': d['date'],
            'close': d['close'],
            'entry': d['close'] + entry / factor,
            'takeProfit': d['close'] + (entry + takeProfit) / factor,
            'stopLoss': d['close'] - stopLoss / factor,
            'active': False,
            'outcome': 0,
        }

        # get result
        for k, d in df.iloc[startAt:].iterrows():
            trade['cnt'] += 1

            # check entry
            if not trade['active'] and d['high'] > trade['entry']:
                trade['active'] = True
                # print i, d['date'], 'entered'

            # check exits
            elif trade['active']:
                # loss?
                if d['low'] < trade['stopLoss']:
                    trade['outcome'] = trade['entry'] - trade['stopLoss']
                    losses.append(trade)
                    # print i, d['date'], 'loss'
                    break
                # win?
                elif d['high'] > trade['takeProfit']:
                    trade['outcome'] = trade['takeProfit'] - trade['entry']
                    wins.append(trade)
                    # print i, d['date'], 'win'
                    break
                else:
                    # print i, d['date'], 'continue', trade['cnt']
                    pass

            # expire at (cannot wait any longer to enter :(
            elif trade['cnt'] >= waitFor:
                break
                # print i, d['date'], 'outta time'

        # if stops are too high, it'll never end (punishment!)
        if trade['outcome'] == 0:
            trade['outcome'] -= 1000 / factor
            losses.append(trade)

    return wins, losses