import pandas as pd
from features import calculateTargets


currency = 'EURUSD'
interval = '60'
factor = 10000

df = pd.read_csv(
    r'../data/' + currency.upper() + interval + '.csv',
    names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
    dtype={'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float', 'volume': 'int'},
    #parse_dates=[[0, 1]],
    # index_col=0,
)
# df = df.iloc[-14400:].reset_index()
print df.tail()

print 'calculating targets...'
calculateTargets(df)

print 'backtesting...'
takeProfit = 110
stopLoss = 290.
entry = 23.
waitFor = 32.
exitAt = 390.

pendings = []
wins = []
losses = []
for i, d in df.iterrows():

    # create trade
    pendings.append({
        'cnt': 0,
        'date': d['date'],
        'close': d['close'],
        'entry': d['close'] + entry / factor,
        'takeProfit': d['close'] + (entry + takeProfit) / factor,
        'stopLoss': d['close'] - stopLoss / factor,
        'active': False,
        'outcome': 0,
    })

    for p, pending in enumerate(pendings):
        pending['cnt'] += 1

        # check entries
        if not pending['active'] and d['high'] > pending['entry']:
            pending['active'] = True

        # check exits
        elif pending['active']:
            # loss?
            if d['low'] < pending['stopLoss']:
                pending['outcome'] = pending['entry'] - pending['stopLoss']
                losses.append(pending)
                del pendings[p]
            # win?
            elif d['high'] > pending['takeProfit']:
                pending['outcome'] = pending['takeProfit'] - pending['entry']
                wins.append(pending)
                del pendings[p]
            # expired?
            elif pending['cnt'] > exitAt:
                loss = pending['entry'] - pending['stopLoss']
                profit = pending['takeProfit'] - pending['entry']
                if profit > loss:
                    pending['outcome'] = profit
                    wins.append(pending)
                else:
                    pending['outcome'] = loss
                    losses.append(pending)
                del pendings[p]

        # cannot wait any longer to enter :(
        elif pending['cnt'] >= waitFor:
            break
            # print i, d['date'], 'outta time'


profit = sum([w['outcome'] for w in wins])
print 'wins', len(wins), round(profit, 4)

loss = sum([l['outcome'] for l in losses])
print 'loss', len(losses), round(loss, 4)

net = profit - loss
npt = net / len(wins + losses)
ratio = len(wins) / (len(wins) + len(losses) + 0.)
print 'net', round(net, 4), 'npt', int(npt * factor), '%', int(ratio * 100)
