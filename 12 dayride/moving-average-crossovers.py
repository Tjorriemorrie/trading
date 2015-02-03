import logging
from os.path import realpath, dirname
import pandas as pd
from sklearn.preprocessing import scale
import matplotlib.pyplot as plt

'''
2015-02-02 18:29:38,285 root     INFO     EURJPY q4 s8 o0.49
2015-02-02 18:29:38,285 root     INFO     EURJPY q4 s12 o0.50
2015-02-02 18:29:38,285 root     INFO     EURJPY q6 s12 o0.50
2015-02-02 18:29:38,285 root     INFO     EURJPY q6 s18 o0.50
2015-02-02 18:29:38,285 root     INFO     EURJPY q8 s16 o0.50
2015-02-02 18:29:38,285 root     INFO     EURJPY q8 s24 o0.50
2015-02-02 18:29:38,285 root     INFO     EURJPY q10 s20 o0.50
2015-02-02 18:29:38,285 root     INFO     EURJPY q10 s30 o0.50
2015-02-02 18:29:38,285 root     INFO     EURJPY q12 s24 o0.51
2015-02-02 18:29:38,286 root     INFO     EURJPY q12 s36 o0.51
2015-02-02 18:29:38,286 root     INFO     EURJPY q14 s28 o0.50
2015-02-02 18:29:38,286 root     INFO     EURJPY q14 s42 o0.50
2015-02-02 18:29:38,286 root     INFO     EURJPY q16 s32 o0.51
2015-02-02 18:29:38,286 root     INFO     EURJPY q16 s48 o0.50
2015-02-02 18:29:38,286 root     INFO     EURJPY q18 s36 o0.50
2015-02-02 18:29:38,286 root     INFO     EURJPY q18 s54 o0.51
2015-02-02 18:29:38,286 root     INFO     USDCHF q4 s8 o0.51
2015-02-02 18:29:38,289 root     INFO     USDCHF q4 s12 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q6 s12 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q6 s18 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q8 s16 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q8 s24 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q10 s20 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q10 s30 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q12 s24 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q12 s36 o0.49
2015-02-02 18:29:38,290 root     INFO     USDCHF q14 s28 o0.49
2015-02-02 18:29:38,290 root     INFO     USDCHF q14 s42 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q16 s32 o0.51
2015-02-02 18:29:38,290 root     INFO     USDCHF q16 s48 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q18 s36 o0.50
2015-02-02 18:29:38,290 root     INFO     USDCHF q18 s54 o0.50
2015-02-02 18:29:38,290 root     INFO     GBPUSD q4 s8 o0.49
2015-02-02 18:29:38,311 root     INFO     GBPUSD q4 s12 o0.50
2015-02-02 18:29:38,311 root     INFO     GBPUSD q6 s12 o0.51
2015-02-02 18:29:38,311 root     INFO     GBPUSD q6 s18 o0.50
2015-02-02 18:29:38,311 root     INFO     GBPUSD q8 s16 o0.50
2015-02-02 18:29:38,311 root     INFO     GBPUSD q8 s24 o0.50
2015-02-02 18:29:38,311 root     INFO     GBPUSD q10 s20 o0.50
2015-02-02 18:29:38,311 root     INFO     GBPUSD q10 s30 o0.50
2015-02-02 18:29:38,311 root     INFO     GBPUSD q12 s24 o0.50
2015-02-02 18:29:38,311 root     INFO     GBPUSD q12 s36 o0.49
2015-02-02 18:29:38,311 root     INFO     GBPUSD q14 s28 o0.50
2015-02-02 18:29:38,312 root     INFO     GBPUSD q14 s42 o0.48
2015-02-02 18:29:38,312 root     INFO     GBPUSD q16 s32 o0.49
2015-02-02 18:29:38,312 root     INFO     GBPUSD q16 s48 o0.49
2015-02-02 18:29:38,312 root     INFO     GBPUSD q18 s36 o0.49
2015-02-02 18:29:38,312 root     INFO     GBPUSD q18 s54 o0.49
2015-02-02 18:29:38,312 root     INFO     EURGBP q4 s8 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q4 s12 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q6 s12 o0.48
2015-02-02 18:29:38,332 root     INFO     EURGBP q6 s18 o0.49
2015-02-02 18:29:38,332 root     INFO     EURGBP q8 s16 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q8 s24 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q10 s20 o0.51
2015-02-02 18:29:38,332 root     INFO     EURGBP q10 s30 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q12 s24 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q12 s36 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q14 s28 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q14 s42 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q16 s32 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q16 s48 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q18 s36 o0.50
2015-02-02 18:29:38,332 root     INFO     EURGBP q18 s54 o0.50
2015-02-02 18:29:38,333 root     INFO     GBPJPY q4 s8 o0.51
2015-02-02 18:29:38,352 root     INFO     GBPJPY q4 s12 o0.51
2015-02-02 18:29:38,353 root     INFO     GBPJPY q6 s12 o0.50
2015-02-02 18:29:38,353 root     INFO     GBPJPY q6 s18 o0.50
2015-02-02 18:29:38,353 root     INFO     GBPJPY q8 s16 o0.50
2015-02-02 18:29:38,353 root     INFO     GBPJPY q8 s24 o0.51
2015-02-02 18:29:38,353 root     INFO     GBPJPY q10 s20 o0.51
2015-02-02 18:29:38,353 root     INFO     GBPJPY q10 s30 o0.49
2015-02-02 18:29:38,353 root     INFO     GBPJPY q12 s24 o0.50
2015-02-02 18:29:38,353 root     INFO     GBPJPY q12 s36 o0.49
2015-02-02 18:29:38,353 root     INFO     GBPJPY q14 s28 o0.50
2015-02-02 18:29:38,353 root     INFO     GBPJPY q14 s42 o0.48
2015-02-02 18:29:38,353 root     INFO     GBPJPY q16 s32 o0.48
2015-02-02 18:29:38,353 root     INFO     GBPJPY q16 s48 o0.49
2015-02-02 18:29:38,353 root     INFO     GBPJPY q18 s36 o0.48
2015-02-02 18:29:38,353 root     INFO     GBPJPY q18 s54 o0.49
2015-02-02 18:29:38,354 root     INFO     AUDUSD q4 s8 o0.50
2015-02-02 18:29:38,390 root     INFO     AUDUSD q4 s12 o0.50
2015-02-02 18:29:38,391 root     INFO     AUDUSD q6 s12 o0.51
2015-02-02 18:29:38,391 root     INFO     AUDUSD q6 s18 o0.51
2015-02-02 18:29:38,391 root     INFO     AUDUSD q8 s16 o0.50
2015-02-02 18:29:38,391 root     INFO     AUDUSD q8 s24 o0.50
2015-02-02 18:29:38,391 root     INFO     AUDUSD q10 s20 o0.50
2015-02-02 18:29:38,391 root     INFO     AUDUSD q10 s30 o0.51
2015-02-02 18:29:38,391 root     INFO     AUDUSD q12 s24 o0.50
2015-02-02 18:29:38,391 root     INFO     AUDUSD q12 s36 o0.51
2015-02-02 18:29:38,391 root     INFO     AUDUSD q14 s28 o0.51
2015-02-02 18:29:38,391 root     INFO     AUDUSD q14 s42 o0.51
2015-02-02 18:29:38,391 root     INFO     AUDUSD q16 s32 o0.51
2015-02-02 18:29:38,391 root     INFO     AUDUSD q16 s48 o0.52
2015-02-02 18:29:38,391 root     INFO     AUDUSD q18 s36 o0.51
2015-02-02 18:29:38,392 root     INFO     AUDUSD q18 s54 o0.51
2015-02-02 18:29:38,392 root     INFO     EURUSD q4 s8 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q4 s12 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q6 s12 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q6 s18 o0.52
2015-02-02 18:29:38,415 root     INFO     EURUSD q8 s16 o0.52
2015-02-02 18:29:38,415 root     INFO     EURUSD q8 s24 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q10 s20 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q10 s30 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q12 s24 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q12 s36 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q14 s28 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q14 s42 o0.53
2015-02-02 18:29:38,415 root     INFO     EURUSD q16 s32 o0.52
2015-02-02 18:29:38,415 root     INFO     EURUSD q16 s48 o0.52
2015-02-02 18:29:38,415 root     INFO     EURUSD q18 s36 o0.51
2015-02-02 18:29:38,415 root     INFO     EURUSD q18 s54 o0.52
2015-02-02 18:29:38,415 root     INFO     USDJPY q4 s8 o0.49
2015-02-02 18:29:38,435 root     INFO     USDJPY q4 s12 o0.51
2015-02-02 18:29:38,436 root     INFO     USDJPY q6 s12 o0.51
2015-02-02 18:29:38,436 root     INFO     USDJPY q6 s18 o0.50
2015-02-02 18:29:38,436 root     INFO     USDJPY q8 s16 o0.50
2015-02-02 18:29:38,436 root     INFO     USDJPY q8 s24 o0.50
2015-02-02 18:29:38,436 root     INFO     USDJPY q10 s20 o0.49
2015-02-02 18:29:38,436 root     INFO     USDJPY q10 s30 o0.49
2015-02-02 18:29:38,436 root     INFO     USDJPY q12 s24 o0.49
2015-02-02 18:29:38,436 root     INFO     USDJPY q12 s36 o0.49
2015-02-02 18:29:38,436 root     INFO     USDJPY q14 s28 o0.48
2015-02-02 18:29:38,436 root     INFO     USDJPY q14 s42 o0.49
2015-02-02 18:29:38,436 root     INFO     USDJPY q16 s32 o0.50
2015-02-02 18:29:38,436 root     INFO     USDJPY q16 s48 o0.50
2015-02-02 18:29:38,436 root     INFO     USDJPY q18 s36 o0.50
2015-02-02 18:29:38,436 root     INFO     USDJPY q18 s54 o0.50
2015-02-02 18:29:38,436 root     INFO     NZDUSD q4 s8 o0.50
2015-02-02 18:29:38,456 root     INFO     NZDUSD q4 s12 o0.50
2015-02-02 18:29:38,456 root     INFO     NZDUSD q6 s12 o0.51
2015-02-02 18:29:38,456 root     INFO     NZDUSD q6 s18 o0.50
2015-02-02 18:29:38,456 root     INFO     NZDUSD q8 s16 o0.50
2015-02-02 18:29:38,456 root     INFO     NZDUSD q8 s24 o0.50
2015-02-02 18:29:38,456 root     INFO     NZDUSD q10 s20 o0.50
2015-02-02 18:29:38,456 root     INFO     NZDUSD q10 s30 o0.49
2015-02-02 18:29:38,456 root     INFO     NZDUSD q12 s24 o0.49
2015-02-02 18:29:38,456 root     INFO     NZDUSD q12 s36 o0.50
2015-02-02 18:29:38,457 root     INFO     NZDUSD q14 s28 o0.50
2015-02-02 18:29:38,457 root     INFO     NZDUSD q14 s42 o0.50
2015-02-02 18:29:38,457 root     INFO     NZDUSD q16 s32 o0.49
2015-02-02 18:29:38,457 root     INFO     NZDUSD q16 s48 o0.51
2015-02-02 18:29:38,457 root     INFO     NZDUSD q18 s36 o0.50
2015-02-02 18:29:38,457 root     INFO     NZDUSD q18 s54 o0.50
2015-02-02 18:29:38,457 root     INFO     USDCAD q4 s8 o0.50
2015-02-02 18:29:38,457 root     INFO     USDCAD q4 s12 o0.49
2015-02-02 18:29:38,478 root     INFO     USDCAD q6 s12 o0.51
2015-02-02 18:29:38,478 root     INFO     USDCAD q6 s18 o0.50
2015-02-02 18:29:38,478 root     INFO     USDCAD q8 s16 o0.50
2015-02-02 18:29:38,478 root     INFO     USDCAD q8 s24 o0.51
2015-02-02 18:29:38,478 root     INFO     USDCAD q10 s20 o0.50
2015-02-02 18:29:38,478 root     INFO     USDCAD q10 s30 o0.50
2015-02-02 18:29:38,479 root     INFO     USDCAD q12 s24 o0.50
2015-02-02 18:29:38,479 root     INFO     USDCAD q12 s36 o0.50
2015-02-02 18:29:38,479 root     INFO     USDCAD q14 s28 o0.50
2015-02-02 18:29:38,479 root     INFO     USDCAD q14 s42 o0.51
2015-02-02 18:29:38,479 root     INFO     USDCAD q16 s32 o0.51
2015-02-02 18:29:38,479 root     INFO     USDCAD q16 s48 o0.51
2015-02-02 18:29:38,479 root     INFO     USDCAD q18 s36 o0.51
2015-02-02 18:29:38,479 root     INFO     USDCAD q18 s54 o0.51
'''

currencies = [
    'AUDUSD',
    'EURGBP',
    'EURJPY',
    'EURUSD',
    'GBPJPY',
    'GBPUSD',
    'NZDUSD',
    'USDCAD',
    'USDCHF',
    'USDJPY',
]


def main():

    results = {}
    for currency in currencies:
        results[currency] = []
        logging.info('Currency: {0}'.format(currency))

        df = loadData(currency)
        # print df

        df = dropOutliers(df)
        # print df

        df = tickTargets(df)
        # print df

        # test 5-20
        for quick in xrange(4, 20, 2):
            for quick_mul in xrange(2, 4):
                slow = quick * quick_mul
                outcome = testCrossOver(df, quick, slow)
                results[currency].append({
                    'quick': quick,
                    'slow': slow,
                    'outcome': outcome,
                })

        # break

    for currency, outcomes in results.iteritems():
        for outcome in outcomes:
            logging.info('{0} q{1} s{2} o{3:.2f}'.format(currency, outcome['quick'], outcome['slow'], outcome['outcome']))


def loadData(currency):
    logging.info('Data: loading {0}...'.format(currency))
    df = pd.read_csv(
        r'{0}/../data/{1}1440.csv'.format(realpath(dirname(__file__)), currency),
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        parse_dates=[[0, 1]],
        index_col=0,
    ).astype(float)
    logging.info('Data: {0} rows loaded'.format(len(df)))
    return df


def dropOutliers(df):
    logging.info('Dropping outliers...')
    size_start = len(df)

    # get range
    df['range'] = df['high'] - df['low']
    # print df

    # get stats
    mean = df.range.mean()
    std = df.range.std()

    # drop outliers
    min_cutoff = mean - std * 2
    max_cutoff = mean + std * 2
    logging.info('Dropping outliers between below {0:.4f} and above {1:.4f}'.format(min_cutoff, max_cutoff))
    df = df[df['range'] > min_cutoff]
    df = df[df['range'] < max_cutoff]

    logging.info('Outliers: {0} removed'.format(size_start - len(df)))
    return df


def tickTargets(df):
    logging.info('Targets: ticks...')

    df['close_tomorrow'] = df['close'].shift(-1)
    # df.dropna(inplace=True)
    # print df.tail()

    df['targets'] = df.apply(lambda x: 'buy' if x['close_tomorrow'] > x['close'] else 'sell', axis=1)

    logging.info('Targets: found')
    return df


def testCrossOver(df, quick, slow):
    logging.info('Crossover: {0}/{1}...'.format(quick, slow))
    df['ma_quick'] = pd.rolling_mean(df['close'], quick)
    df['ma_slow'] = pd.rolling_mean(df['close'], slow)
    df.dropna(inplace=True)
    # print df
    df['target_w_ma'] = df.apply(lambda x: (x['ma_quick'] > x['ma_slow'] and x['targets'] == 'buy') or (x['ma_quick'] < x['ma_slow'] and x['targets'] == 'sell'), axis=1)
    # print df
    corrects = len(df[df['target_w_ma'] == True])
    logging.info('correct {0} out of {1}'.format(corrects, len(df)))
    outcome = corrects / (len(df) + 0.)
    logging.info('Crossover: {0}'.format(outcome))
    return outcome


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main()