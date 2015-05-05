import logging as log
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, scale
from sklearn.cross_validation import cross_val_score, train_test_split
from sklearn.ensemble import GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.svm import SVR
import os
import pickle
from pprint import pprint
import operator
import json


# FOLDER = '20150505_tpc_sawgrass'
FOLDER = '20150423_zurich_classic_of_new_orleans'
YEAR_START = 2000
YEAR_END = 2014

def main():
    log.info('main start')

    dfs = []
    for year in range(YEAR_START+1, YEAR_END+1):
        dfs.append(loadHistory(year))
    # print dfs
    df = pd.concat(dfs, ignore_index=True)
    # print df.head(1)
    # print df['score']
    log.info('{} total rows'.format(len(df)))

    # clean player data
    df_cleaned = cleanPlayerData(df)
    df_cleaned.to_csv('{}/data.csv'.format(FOLDER))

    # get labels and features
    log.info('getting labels and features...')
    labels = df_cleaned['score']
    print 'labels\n', labels
    # print df_merged.columns[-10:]
    df_cleaned = df_cleaned.drop('score', axis=1).astype(float)
    features = scale(df_cleaned)
    # print df_merged.columns[-10:]
    print 'features\n', features[0]

    X_train, X_test, y_train, y_test = train_test_split(features, labels)

    # CV
    # clf = GradientBoostingRegressor()
    clf = SVR(kernel='linear')
    # clf = ExtraTreesRegressor(n_estimators=1000)
    cv = cross_val_score(clf, X_train, y_train, cv=5, scoring='r2')
    cv = [abs(n) for n in cv]
    log.info('CV mean {} std {}'.format(np.mean(cv), np.std(cv)))
    # print 'cv', cv

    # train
    clf.fit(X_train, y_train)
    print 'score', clf.score(X_test, y_test)

    # predict
    prediction = predictCurrent(clf, YEAR_END+1, df_cleaned.columns)

    # calculate winnings
    # calculateWinnings(prediction)

    log.info('main end')


def loadHistory(year):
    log.info('load history {}'.format(year))
    df_tourney = loadTourney(year)
    df_players = loadPlayers(year-1, df_tourney)
    df_players['score'] = df_tourney
    # print df_players
    log.info('load history {}'.format(len(df_players)))
    return df_players


def loadTourney(year):
    log.info('load tourney {}'.format(year))
    with open('{}/{}.pkl'.format(FOLDER, year), 'r') as f:
        data = pickle.load(f)
    df = pd.DataFrame.from_dict(data)
    # print df.head(1)
    df = df.set_index('player_id')
    # print df.head(1)

    df['score'] = df['score'].astype(float)

    # top half labels
    df_top = df[np.isfinite(df['r4'])]
    df_top['pos'] = df_top['pos'].apply(lambda x: float(x.replace('T', '')))
    # print tdf_top.sort('score')
    # df_top['score_scaled'] = MinMaxScaler(feature_range=(0.6, 1.)).fit_transform(df_top['score'].astype(float))[::-1]
    df_top['score_scaled'] = scale(df_top['score'] / df_top['pos'])
    # print df_top.sort('score')

    # bottom half
    df_bot = df[df['pos'] == 'CUT']
    # print tdf_bot.sort('score')
    df_bot['score_scaled'] = MinMaxScaler(feature_range=(0., 0.4)).fit_transform(df_bot['score'].astype(float))[::-1]
    # print tdf_bot

    # combine labels
    # df = pd.concat([df_top, df_bot])
    df = df_top

    # df['score_scaled'] = 0
    # df = df.set_value(df.index[0], 'score_scaled', 1)

    # print df
    log.info('load tourney ended')
    return df['score_scaled']


def loadPlayers(year, df_tourney):
    log.info('load players {}'.format(year))

    df_players = pd.DataFrame()
    for player_id, score_scaled in df_tourney.iteritems():
        player_file = 'players/{}/{}.pkl'.format(year, player_id)
        # print player_file
        if os.path.isfile(player_file):
            with open(player_file, 'r') as f:
                player_data = pickle.load(f)
                player_data['player_id'] = player_id
                # print player_data
                df_players = df_players.append(player_data, ignore_index=True)
                # break
        else:
            print 'could not load {}'.format(player_id)
    df_players = df_players.set_index('player_id')
    # print df_players.head(1)
    log.info('load players ended')

    return df_players


def cleanPlayerData(df):
    log.info('cleaning player data...')
    print 'columns', df.columns

    # # take columns which is >20% populated
    # cols = []
    # for col in df.columns:
    #     #print col, df_players[col].isnull().sum()
    #     if df[col].isnull().sum() > len(df) * 0.2:
    #         cols.append(col)
    #     # elif 'recap_' not in col and col not in ['score']:
    #     #     cols.append(col)
    # log.info('{} total columns vs {} bad columns'.format(len(df.columns), len(cols)))
    # # print 'dropping', cols
    # df_players_cleaned = df.drop(cols, axis=1)

    # only use golf ranking
    df_players_cleaned = df[[
        'recap_official_world_golf_ranking',
        'off the tee_driving_distance',
        # 'off the tee_left_rough_tendency',
        # 'off the tee_right_rough_tendency',
        'score'
    ]]

    # drop players with missing data
    df_players_cleaned_dropped = df_players_cleaned.dropna()
    log.info('{} players left from {}'.format(len(df_players_cleaned_dropped), len(df_players_cleaned)))

    log.info('player data cleaned...')
    return df_players_cleaned_dropped


def predictCurrent(clf, year, cols_to_use):
    log.info('predicting')

    # load players
    df = pd.DataFrame()
    with open('{}/{}.pkl'.format(FOLDER, year), 'r') as f:
        player_ids = pickle.load(f)
        # pprint(player_ids)

        for player_id in player_ids:
            player_file = 'players/{}/{}.pkl'.format(year-1, player_id)
            if not os.path.isfile(player_file):
                print 'could not load {}'.format(player_id)
            else:
                with open(player_file, 'r') as f:
                    player_data = pickle.load(f)
                    player_data['player_id'] = player_id
                    df = df.append(player_data, ignore_index=True)
    df = df.set_index('player_id')
    df = df[cols_to_use]
    # print df

    # clean features
    log.info('Cleaning player list from {}'.format(len(df)))
    df_cleaned = df.dropna()
    df_cleaned.to_csv('{}/current.csv'.format(FOLDER))
    log.info('Cleaning player list to {}'.format(len(df_cleaned)))

    # scale features
    log.info('scaling features')
    features = scale(df_cleaned.astype(float))
    log.info('features scaled')

    # predicting
    log.info('Predicting...')
    prediction = pd.DataFrame(index=df_cleaned.index)
    prediction['p'] = clf.predict(features)
    prediction['p_mm'] = MinMaxScaler(feature_range=(0., 1.)).fit_transform(prediction['p'].astype(float))
    prediction = prediction.sort('p_mm')[:70]
    prediction['p_mm_i'] = 1 - prediction['p_mm']
    prediction['p_mm_i_w'] = prediction['p_mm_i'] / prediction['p_mm_i'].sum()
    prediction['odds'] = (1 - prediction['p_mm_i_w']) / prediction['p_mm_i_w']
    print prediction

    # add back in players' names
    log.info('Adding back in players names for {}'.format(len(prediction)))
    with open('players/_list.pkl', 'r') as f:
        players = pickle.load(f)
        players = {v: k for k, v in players.iteritems()}
        #print players
        prediction['player_name'] = [players[i] if i in players else None for i in prediction.index.values]
    prediction_found = prediction.dropna()
    log.info('Adding back in players names finally {}'.format(len(prediction_found)))
    # print prediction_found
    for player_id, row in prediction_found.sort('odds').iterrows():
        print '{:.0f} {}'.format(row['odds'], row['player_name'])

    # save file
    prediction_found.sort('odds').to_csv('{}/prediction.csv'.format(FOLDER))

    # feature importances
    # log.info('Feature importances:')
    # features_imps = {cols_to_use[i]: val for i, val in enumerate(clf.feature_importances_)}
    # features_imps = sorted(features_imps.items(), key=operator.itemgetter(1))
    # for f_name, f_value in features_imps:
    #     log.info('{:.2f}% {}'.format(f_value * 100, f_name))


    log.info('predicted')
    return prediction_found


def calculateWinnings(prediction):
    log.info('calculating winnings...')

    # load odds
    file_odds = '{}/{}_odds.json'.format(FOLDER, YEAR_END + 1)
    with open(file_odds, 'r') as fp:
        odds = pd.DataFrame.from_dict(json.load(fp)['odds'])
    # print odds

    # clean odds
    odds['betting_odds'] = odds.betting_odds.apply(lambda x: float(x.split('/')[0]))
    odds['betting_prob'] = odds.betting_odds.apply(lambda x: 1 / (x + 1.))
    # print odds
    # print prediction

    # calculate revenue
    tax = 0.01
    df = prediction.merge(odds, left_on='player_name', right_on='player_name', left_index=True)
    # print df
    df['revenue'] = df['p_mm_i_w'] * df['betting_odds'] * (1 - tax)
    df = df.sort('revenue', ascending=False)
    print df[['player_name', 'odds', 'betting_odds', 'revenue']]

    log.info('winnings calculated')


if __name__ == '__main__':
    log.basicConfig(
        level=log.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main()