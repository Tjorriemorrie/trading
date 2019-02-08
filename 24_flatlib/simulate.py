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

    comb = pd.merge(ndq['is_higher'], astro, how='left', left_index=True, right_index=True)
    comb.dropna(inplace=True)
    print('data frames merged')

    Y = comb['is_higher']
    X = comb.drop(['is_higher'], axis=1)
    print('X and Y extracted')

    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.33, random_state=42)

    # random forest
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)
    yframe = y_test.to_frame()
    yframe['pred'] = clf.predict(X_test)

    backwards = pd.merge(ndq, yframe['pred'], how='left', left_index=True, right_index=True)
    backwards.dropna(inplace=True)
    print('dropped non predictions')

    backwards['movement'] = backwards['Index Value 5'] - backwards['Index Value']
    # backwards['mov_high'] = 1 if backwards['is_higher'] else -1
    backwards['gain'] = backwards['movement']
    backwards.loc[backwards['is_higher'] == backwards['pred'], 'gain'] = backwards['movement'] * -1
    # backwards['gain'] = backwards['movement'] * backwards['mov_high']
    print('gain calculated')

    print(f'gained sum {backwards["gain"].sum()} and {backwards["gain"].mean()} per day')

    print('ended simulation')


if __name__ == '__main__':
    main()
