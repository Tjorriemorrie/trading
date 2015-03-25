import logging
import numpy as np
import argparse
import pandas as pd
from time import time
from pprint import pprint
from random import random, choice, shuffle, randint

from main import loadData, loadQ, saveQ, getBackgroundKnowledge, summarizeActions
from world import DATA, PERIODS, ACTIONS, getState, getReward

'''
https://www.inovancetech.com/strategyEvaluation2.html
'''

'''
2015-03-20 15:09:19,521 root     WARNING  probabilities:
2015-03-20 15:09:19,522 root     INFO     1: 12.50% every 8
2015-03-20 15:09:19,522 root     INFO     2: 6.25% every 16
2015-03-20 15:09:19,522 root     INFO     3: 3.12% every 32
2015-03-20 15:09:19,522 root     INFO     4: 1.56% every 64
2015-03-20 15:09:19,522 root     INFO     5: 0.78% every 128
2015-03-20 15:09:19,522 root     INFO     6: 0.39% every 256
2015-03-20 15:09:19,522 root     INFO     7: 0.20% every 512
2015-03-20 15:09:19,522 root     INFO     8: 0.10% every 1024
2015-03-20 15:09:19,522 root     INFO     9: 0.05% every 2048

1849
1: 231
2: 116
3: 58
4: 29
5: 14
6: 7
7: 4
8: 2
9: 1

{'False_1': 248,
 'False_2': 120,
 'False_3': 66,
 'False_4': 20,
 'False_5': 14,
 'False_6': 3,
 'False_7': 2,
 'False_8': 3,
 'True_1': 234,
 'True_2': 115,
 'True_3': 64,
 'True_4': 32,
 'True_5': 21,
 'True_6': 5,
 'True_7': 3,
 'True_8': 2}

1   1
2   2
3   4
4   8
5   16
6   32
7   64
8   128
9   256

'''

def main():
    for info in DATA:
        currency = info['currency']
        min_trail = info['trail']
        interval = info['intervals'][0]
        pip_mul = info['pip_mul']
        logging.info(currency)

        df = loadData(currency, interval, 'all')
        # print df

        df['yesterday'] = df['close'].shift(1)
        # print df

        df['up'] = df.apply(lambda x: True if x['close'] - x['yesterday'] > 0 else False, axis=1)
        df.dropna(inplace=True)
        print df

        results = {}
        run_dir = True
        run_len = 0
        for idx, row in df.iterrows():
            # logging.info(row['up'])
            if row['up'] != run_dir:
                key = '{0}'.format(run_len)
                if key not in results:
                    results[key] = 0
                results[key] += 1

                run_dir = row['up']
                run_len = 1
            else:
                run_len += 1
        pprint(results)

        logging.warn('probabilities:')
        for n in xrange(1, 10):
            p = 0.5**(n+1)
            every = 1/p
            expecting = len(df) / every
            logging.info('{0}: {1:.2f}% every {2:.0f} expecting {3:.0f}'.format(n, p * 100, every, expecting))

        break



if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main()