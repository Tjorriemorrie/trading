import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model
from features import calculateTargets
from simulate import backtest
from pprint import pprint

currency = 'EURUSD'
interval = '30'
factor = 10000

df = pd.read_csv(
    r'../../data/' + currency.upper() + interval + '.csv',
    names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
    dtype={'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float', 'volume': 'int'},
    #parse_dates=[[0, 1]],
    # index_col=0,
)
df = df.iloc[-15000:].reset_index()
print df

print 'calculating targets...'
calculateTargets(df)


samples = 1000
takeProfit = 260.
stopLoss = 291.
entry = 30.
waitFors = [wf + 0. for wf in range(27, 88, 3)]
totalNpt = []
totalRat = []
for waitFor in waitFors:
    print '\nwait for', waitFor
    wins, losses = backtest(df, takeProfit, stopLoss, entry, waitFor, factor, samples)
    print 'quantity', len(wins) + len(losses), '/', samples
    if len(wins) + len(losses) < 1:
        print 'no trades!'
        continue

    profit = sum([w['outcome'] for w in wins])
    print 'wins', len(wins), round(profit, 4)

    loss = sum([l['outcome'] for l in losses])
    print 'loss', len(losses), round(loss, 4)

    net = profit - loss
    npt = int((net / len(wins + losses)) * factor)
    ratio = len(wins) / (len(wins) + len(losses) + 0.)
    print 'net', round(net, 4), 'npt', npt, '%', int(ratio * 100)

    totalNpt.append(net)
    totalRat.append(ratio)

print '\n'
#pprint(totalNpt)

N = len(totalNpt)
#totalNpt = (20, 35, 30, 35, 27)
#menStd =   (2, 3, 4, 1, 2)

ind = np.arange(N)  # the x locations for the groups
width = 0.35       # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(ind, totalNpt, width, color='r')

#womenMeans = (25, 32, 34, 20, 25)
#womenStd =   (3, 5, 2, 3, 3)
rects2 = ax.bar(ind+width, totalRat, width, color='y')

# add some text for labels, title and axes ticks
ax.set_ylabel('Pips')
ax.set_title('Results')
ax.set_xticks(ind + width)
ax.set_xticklabels(map(int, waitFors))

#ax.legend(
#    (rects1[0]),
#    ('Npt',),
#)

def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha='center', va='bottom')

#autolabel(rects1)
#autolabel(rects2)

plt.show()
