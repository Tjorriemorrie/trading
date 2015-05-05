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

        # set labels
        labels = getLabels(df)
        # print labels

        # print df.tail()
        # print labels.tail()

        # split and scale
        X_train, X_test, y_train, y_test = splitAndScale(df, labels)
        # print X_test
        # print y_test

        # loading regressor
        clf = joblib.load('models/{0}.gbrt'.format(item['currency']))
        log.info('Classifier loading')

        # predict last day
        prediction = clf.predict(X_test[-1])
        predict_proba = clf.predict_proba(X_test[-1])
        log.warn('{0} {1} {2} {3}'.format(df.ix[-1].name, item['currency'], prediction[0], max(predict_proba[0])))


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # args = parser.parse_args()

    log.basicConfig(
        level=log.WARN,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main()