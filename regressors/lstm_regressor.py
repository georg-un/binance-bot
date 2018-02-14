import configparser
import sqlite3

import numpy as np
import tensorflow as tf

from sklearn.preprocessing import MinMaxScaler

from general.general_modules import getlist
from regressors.modules.regression_modules import transform_fn
from regressors.modules.regression_modules import train_input_fn
from regressors.modules.regression_modules import get_feature_columns
from regressors.modules.lstm_function import lstm_model



# set up config parser
configParser = configparser.ConfigParser()

# read config-file
configParser.read(r'config.txt')

db_path = configParser.get('config', 'db_path')
symbols = getlist(configParser.get('symbols', 'symbol_list'))
intervals = getlist(configParser.get('intervals', 'interval_list'))

BATCH_SIZE = 5
F_HORIZON = 1


# SET UP DATABASE CONNECTION

# connect to database
db_con = sqlite3.connect(db_path)

with db_con:
    for symbol in symbols:
        cur = db_con.cursor()
        cur.execute('SELECT {0}_15m.close, {0}_15m_feat.* FROM {0}_15m_feat JOIN {0}_15m ON {0}_15m.t_open={0}_15m_feat.t_open'.format(symbol))
        data = np.array(cur.fetchall()).astype('float32')

data = data[100:, :]


# PREPARE DATA

# split data into test and training
test_split = int(len(data) * 0.75)

# create training data
train_X = data[:test_split, 2:]
train_y = data[F_HORIZON:F_HORIZON+test_split, 0]

# create test data
test_X = data[test_split+1: len(data)-F_HORIZON-1, 2:]
test_y = data[test_split+1+F_HORIZON: len(data)-1, 0]


# scale data
scaler = MinMaxScaler()
train_X = scaler.fit_transform(train_X)
test_X = scaler.fit_transform(test_X)

# transform data
train_X, train_y = transform_fn(train_X, train_y)
test_X, test_y = transform_fn(test_X, test_y)


# create feature column tensor
feature_columns = get_feature_columns(train_X)


# MODEL

# define regressor
regressor = tf.estimator.Estimator(model_fn=lstm_model,
                                   model_dir='/home/georg/test/lstm',
                                   params={
                                       'feature_columns': feature_columns,
                                       'batch_size': BATCH_SIZE,
                                       'learning_rate': 0.00001
                                   })

# train model
regressor.train(input_fn=lambda: train_input_fn(train_X, train_y, BATCH_SIZE), steps=int(len(train_y)/BATCH_SIZE))
