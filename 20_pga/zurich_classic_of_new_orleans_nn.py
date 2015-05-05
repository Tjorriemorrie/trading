import pickle
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
import sknn.mlp

# load tournament data
with open('tourns/zurich_classic_of_new_orleans/2014.pkl', 'r') as f:
    tdf = pd.DataFrame.from_dict(pickle.load(f)).set_index('player_name')
    tdf = tdf[np.isfinite(tdf['r4'])]
    tdf['pos'] = tdf['pos'].apply(lambda x: float(x.replace('T', '')))

# load player data
with open('stats/2014/points/fedexcupstandings.pkl', 'r') as f:
    pdf = pd.DataFrame.from_dict(pickle.load(f)).set_index('player_name')

# merge and clean
df = pdf.drop(['player_id', 'player_url', 'rank_last_week', 'rank_this_week', 'reset_points', 'year'], axis=1)
df = df.join(tdf.pos, how='right')
df = df.dropna(axis=0, how='any')
# print df

# sample data
X_train, X_test, y_train, y_test = train_test_split(df.iloc[:, :-1], df.iloc[:, -1])
print X_train

# create nn
nn = sknn.mlp.MultiLayerPerceptronClassifier(
    layers=[("Rectifier", 100), ("Linear",)],
    learning_rate=0.02,
    n_iter=10)

# train and score
nn.fit(X_train, y_train)
# nn.predict(X_test)
print nn.score(X_test, y_test)