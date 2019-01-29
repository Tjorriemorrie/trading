import numpy as np
import pandas as pd
import quandl


def download():
    ndq = quandl.get("NASDAQOMX/COMP-NASDAQ",
                     trim_start='1998-03-01',
                     trim_end='2018-04-03')
    ndq.to_csv('nasdaq.csv')
    print('done')


def main():
    ndq = pd.read_csv('nasdaq.csv')
    ndq['rolmax'] = ndq['Index Value'].rolling(5).max().shift(-5)
    ndq['rolmin'] = ndq['Index Value'].rolling(5).min().shift(-5)
    ndq = ndq.dropna()
    # ndq['to_use'] = 'buy' if ndq['rolmax'] - ndq['Index Value'] > ndq['Index Value'] - ndq['rolmin'] else 'short'
    ndq['max_to_index'] = ndq['rolmax'] - ndq['Index Value']
    ndq['min_to_index'] = ndq['Index Value'] - ndq['rolmin']
    ndq['to_use'] = np.where(ndq['max_to_index'] > ndq['min_to_index'], 'long', 'short')
    print(ndq)
    ndq.to_csv('nasdaq_lbl.csv')
    print('done')


if __name__ == '__main__':
    # download()
    main()
