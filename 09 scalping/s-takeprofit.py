import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model
from features import calculateTargets
from simulate import backtest
from pprint import pprint

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
#bullMean = df['targetBull'].mean()
#bullStd = df['targetBull'].std()
#print 'high mean std', bullMean, bullStd
bearMean = df['targetBear'].mean()
bearStd = df['targetBear'].std()
print 'bear mean std', bearMean, bearStd

print 'backtesting...'
takeProfits = [tp + 0. for tp in range(400, 601, 10)]
stopLoss = 540.
entry = 20.
waitFor = 95.
exitAt = 530.
totalNpt = []
totalRat = []
for takeProfit in takeProfits:
    print '\ntakeProfit', takeProfit
    wins, losses = backtest(df, takeProfit, stopLoss, entry, waitFor, exitAt, factor)

    profit = sum([w['outcome'] for w in wins])
    print 'wins', len(wins), round(profit, 4)

    loss = sum([l['outcome'] for l in losses])
    print 'loss', len(losses), round(loss, 4)

    net = profit - loss
    npt = int((net / len(wins + losses)) * factor)
    ratio = len(wins) / (len(wins) + len(losses) + 0.)
    print 'net', round(net, 4), 'npt', npt, '%', int(ratio * 100)

    totalNpt.append(npt)
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
ax.set_xticklabels(map(int, takeProfits))

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
