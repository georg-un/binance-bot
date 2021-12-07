# LOAD LIBRARIES & FILES

# load libraries
import configparser
import sqlite3
import numpy as np
import pandas as pd
import xgboost as xgb
import sklearn
import math
#from xgboost.sklearn import XGBRegressor
from sklearn.metrics import accuracy_score


# READ CONFIG

def getlist(option, sep=',', chars=None):
    """Return a list from a ConfigParser option. By default,
       split on a comma and strip whitespaces."""
    return [chunk.strip(chars) for chunk in option.split(sep)]


# set up config parser
configParser = configparser.ConfigParser()

# read config-file
configParser.read(r'config.txt')

db_path = configParser.get('config', 'db_path')
symbols = getlist(configParser.get('symbols', 'symbol_list'))
intervals = getlist(configParser.get('intervals', 'interval_list'))


# SET UP DATABASE CONNECTION

# connect to database
db_con = sqlite3.connect(db_path)


#with db_con:
#    cur = db_con.cursor()
#    cur.execute('SELECT * FROM ADAETH_15m_feat')
#    test = cur.fetchall()


with db_con:
    cur = db_con.cursor()
    cur.execute('SELECT ADAETH_15m.close, ADAETH_15m_feat.* FROM ADAETH_15m_feat JOIN ADAETH_15m ON ADAETH_15m.t_open=ADAETH_15m_feat.t_open')
    data = cur.fetchall()
    cur.execute("PRAGMA table_info('ADAETH_15m_feat')")
    lables = cur.fetchall()


data = pd.DataFrame(data)
#data.info()
data = data.values

lables = [i[1] for i in lables]


X = data[0:(data.shape[0]-1-4), 1:(data.shape[1]-1)]
y = data[4:(data.shape[0]-1), 0]

split_index = math.floor((len(data)/3)*2)

X_train = X[0:split_index, :]
X_test = X[(split_index+1):(len(X)-1), :]

y_train = y[0:split_index]
y_test = y[(split_index+1):(len(y)-1)]


#train = xgb.DMatrix(X_train, label=y_train)
#test = xgb.DMatrix(X_test, label=y_test)


#nrow = data.shape[0]
#ncol = data.shape[1]
#train = data[100:2*(int(nrow/3)), :]
#test = data[2*(int(nrow/3)):(nrow-1), :]


#X_train = train[:, 1:(train.shape[1]-1)]
#y_train = train[:, 0]
#X_test = test[:, 1:(test.shape[1]-1)]
#y_test = test[:, 0]








#xgbreg =xgb.XGBRegressor(base_score=0.5, booster='gbtree', colsample_bylevel=1,
#                         colsample_bytree=1, gamma=0, learning_rate=0.1, max_delta_step=0,
#                         max_depth=3, min_child_weight=1, missing=None, n_estimators=100,
#                         n_jobs=1, nthread=-2, objective='reg:linear', random_state=0,
#                         reg_alpha=0, reg_lambda=1, scale_pos_weight=1, seed=0,
#                         silent=True, subsample=1)


xgbreg = xgb.XGBRegressor(learning_rate=0.1, n_estimators=1000,
                          max_depth=3, min_child_weight=1,
                          gamma=0, subsample=1,
                          colsample_bytree=1, objective="reg:linear",
                          nthread=-1, scale_pos_weight=1, random_state=27)


#xgbreg = xgb.XGBRegressor()


xgbreg.fit(X_train, y_train, verbose=True)


y_pred = xgbreg.predict(X_test)


print('Mean absolute error: ' + str(sklearn.metrics.mean_absolute_error(y_test, y_pred)))
print('R²: ' + str(sklearn.metrics.explained_variance_score(y_test, y_pred)))
print('Score: ' + str(xgbreg.score(X_test, y_test)))
