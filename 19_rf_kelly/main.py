import logging as log
import pandas as pd
import pandas.io.data as web



DATA = [
    {'currency': 'AUDUSD', 'timeframe': 1440},
    {'currency': 'EURGBP', 'timeframe': 1440},
    {'currency': 'EURJPY', 'timeframe': 1440},
    {'currency': 'EURUSD', 'timeframe': 1440},
    {'currency': 'GBPJPY', 'timeframe': 1440},
    {'currency': 'GBPUSD', 'timeframe': 1440},
    {'currency': 'NZDUSD', 'timeframe': 1440},
    {'currency': 'USDCAD', 'timeframe': 1440},
    {'currency': 'USDCHF', 'timeframe': 1440},
    {'currency': 'USDJPY', 'timeframe': 1440},
]


def loadDataFred(currency, timeframe):
    log.info('Data: FRED loading...')
    df = web.get_data_fred('DEXJPUS')
    print df
    log.info('Data: FRED loaded')
