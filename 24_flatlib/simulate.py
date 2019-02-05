from datetime import datetime, timedelta
from typing import NoReturn

import pandas as pd
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

ASTRO_FILE = 'astro.csv'
NASDAQ_FILE = 'nasdaq5.csv'


def main() -> NoReturn:
    print('starting simulation')

    # load
    ndq = pd.read_csv(NASDAQ_FILE)
    ndq.set_index('Trade Date', inplace=True)
    astro = pd.read_csv(ASTRO_FILE)
    astro.set_index('date', inplace=True)
    print('data frames loaded')

    X_train, X_test, y_train, y_test = train_test_split(
        astro, ndq['los'], test_size=0.33, random_state=42)

    # random forest
    clf = RandomForestClassifier()

    print('ended simulation')


if __name__ == '__main__':
    main()
