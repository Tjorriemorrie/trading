import pathlib
import pandas as pd

import quandl

DATA_FILE = 'nasdaq_data.csv'
DATA_TRF = 'nasdaq5.csv'


def download_data():
    if pathlib.Path(DATA_FILE).exists():
        print('data file already downloaded')
        return
    ndq = quandl.get("NASDAQOMX/COMP-NASDAQ", trim_start='2000-01-01', trim_end='2019-02-01')
    print('data downloaded ')
    ndq.to_csv(DATA_FILE)
    print('data saved')


def transform_data():
    ndq = pd.read_csv(DATA_FILE)
    print('data loaded')

    ndq['Trade Date'] = pd.to_datetime(ndq['Trade Date']).dt.date
    ndq.set_index('Trade Date', inplace=True)
    print('date set as index')

    ndq['Index Value 5'] = ndq['Index Value'].shift(-5)
    ndq.dropna(inplace=True)
    print('Five days ahead price shifted')

    ndq['is_higher'] = ndq['Index Value 5'] > ndq['Index Value']
    print('is higher value created')

    ndq.to_csv(DATA_TRF)
    print('data saved')

    print('done')


if __name__ == '__main__':
    download_data()
    transform_data()
