import os
import logging
import pandas as pd

logging.getLogger(__name__)


class World():

    def __init__(self):
        self.training_set, self.validation_set = self.load_data()
        self.state_index = 0

    def load_data(self):
        df = pd.read_csv('numerai_training_data.csv')
        logging.debug('\n{}'.format(df.head()))

        # analyze before split
        self.analyze(df)

        # split
        training_set = df[df['validation'] == 0]
        logging.debug('Training set:\n{}'.format(training_set.head()))

        validation_set = df[df['validation'] == 1]
        logging.debug('Validation set:\n{}'.format(validation_set.head()))

        return training_set, validation_set

    def analyze(self, df):
        logging.info('analyzing')

        for n in range(1, 15):
            df['p{}'.format(n)] = df['f{}'.format(n)]

    def state(self):
        row = self.training_set.iloc[0]
        logging.info('State: periods {0}...'.format(periods))

        s = []

        for x in periods:
            s.append('1' if row['ma_{0}_bullish'.format(x)] else '0')
            s.append('1' if row['ma_{0}_divergence'.format(x)] else '0')
            s.append('1' if row['ma_{0}_magnitude'.format(x)] else '0')
    
            for y in periods:
                if y <= x:
                    continue
                s.append('1' if row['ma_{0}_crossover_{1}_bullish'.format(x, y)] else '0')
                s.append('1' if row['ma_{0}_crossover_{1}_divergence'.format(x, y)] else '0')
                s.append('1' if row['ma_{0}_crossover_{1}_magnitude'.format(x, y)] else '0')
        # logging.debug('State: moving average {0}'.format(s))
    
        s_string = ''.join(s)
        logging.debug('State: {0}'.format(s_string))
    
        return s_string




def getReward(df, a, pip_mul, std):
    a_trade, a_limit, a_stop_loss, a_take_profit = a.split('-')
    logging.info('Reward: {0} L:{1} SL:{2} TP:{3}'.format(a_trade, a_limit, a_stop_loss, a_take_profit))
    logging.debug('Std: {0:.4f}'.format(std))

    entry = df.iloc[0]['close']
    logging.debug('Reward: entry at {0:.4f}'.format(entry))
    if a_trade == 'buy':
        limit = entry + std * float(a_limit)
        stop_loss = limit - std * float(a_stop_loss)
        take_profit = limit + std * float(a_take_profit)
    elif a_trade == 'sell':
        limit = entry - std * float(a_limit)
        stop_loss = limit + std * float(a_stop_loss)
        take_profit = limit - std * float(a_take_profit)
    else:
        raise Exception('Unknown trade type {0}'.format(a_trade))
    logging.debug('Reward: limit at {0:.4f}'.format(limit))
    logging.debug('Reward: stop loss at {0:.4f}'.format(stop_loss))
    logging.debug('Reward: take profit at {0:.4f}'.format(take_profit))

    ticks = -1
    r = 0
    entered = False
    for i, row in df.iterrows():
        ticks += 1
        logging.debug('Reward: {0} {1} {2:.4f} TP={3:.4f} SL={4:.4f}'.format(a_trade, i, row['close'], take_profit, stop_loss))
        # buy
        if a_trade == 'buy':
            if entered:
                # stop loss?
                if row['low'] <= stop_loss:
                    logging.debug('Reward: stop loss triggered: low [{0:.4f}] < stop_loss [{1:.4f}]'.format(row['low'], stop_loss))
                    r += stop_loss - limit 
                    break
                # take profit?
                if row['high'] >= take_profit:
                    logging.debug('Reward: take profit triggered: high [{0:.4f}] > take_profit [{1:0.4f}]'.format(row['high'], take_profit))
                    r += take_profit - limit
                    break
            elif ticks > 1:
                if row['high'] >= limit:
                    entered = True
        # sell
        if a_trade == 'sell':
            if entered:
                # stop loss?
                if row['high'] >= stop_loss:
                    logging.debug('Reward: stop loss triggered: high [{0:.4f}] > stop_loss [{1:.4f}]'.format(row['high'], stop_loss))
                    r += limit - stop_loss
                    break
                # take profit?
                if row['low'] <= take_profit:
                    logging.debug('Reward: take profit triggered: low [{0:.4f}] > take_profit [{1:0.4f}]'.format(row['low'], take_profit))
                    r += limit - take_profit
                    break
            elif ticks > 1:
                if row['low'] <= limit:
                    entered = True

    r -= (ticks * 2) / pip_mul

    return r, ticks
