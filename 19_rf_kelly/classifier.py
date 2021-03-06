import logging as log
import pandas as pd
import numpy as np
from pprint import pprint
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.externals import joblib
from main import DATA, loadData, getLabels, splitAndScale, addEwma, addRsi


FIBOS = [5, 13, 34]

def main():
    for item in DATA:
        df = loadData(item['currency'], item['timeframe'])
        # print df

        # adding indicators
        addEwma(df, FIBOS)
        addRsi(df, FIBOS)
        # print df
        # break

        # set labels
        labels = getLabels(df)
        # print labels

        print df
        print labels

        # split and scale
        X_train, X_test, y_train, y_test = splitAndScale(df, labels)
        print X_train
        print y_train

        # fitting regressor
        clf = GradientBoostingClassifier()
        clf.fit(X_train, y_train)
        log.info('Classifier fitted')

        # saving
        joblib.dump(clf, 'models/{0}.gbrt'.format(item['currency']), compress=9)
        log.info('Classifier saved')


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # args = parser.parse_args()

    log.basicConfig(
        level=log.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main()