import configparser
import sqlite3

import numpy as np
import tensorflow as tf

from sklearn.preprocessing import MinMaxScaler

from general.general_modules import getlist
from regressors.modules.regression_modules import transform_fn
from regressors.modules.regression_modules import train_input_fn
from regressors.modules.regression_modules import get_default_feature_columns
from regressors.modules.lstm_function import lstm_model
from regressors.modules.regression_modules import combine_symbols


# READ CONFIG

# set up config parser
configParser = configparser.ConfigParser()

# read config-file
configParser.read(r'config.txt')

db_path = configParser.get('config', 'db_path')
symbols = getlist(configParser.get('symbols', 'symbol_list'))
intervals = getlist(configParser.get('intervals', 'interval_list'))

BATCH_SIZE = 5
F_HORIZON = 1
TEST_RATIO = 0.75
LEARNING_RATE = 0.0001


# MODEL

# define regressor
regressor = tf.estimator.Estimator(model_fn=lstm_model,
                                   model_dir='/home/georg/test/lstm',
                                   params={
                                       'feature_columns': get_default_feature_columns(),
                                       'batch_size': BATCH_SIZE,
                                       'learning_rate': LEARNING_RATE
                                   })


# PREPARE DATA

# connect to database
db_con = sqlite3.connect(db_path)

# set up dictionaries
training_dict = {}
test_dict = {}

# download feature and price data for each symbol, split in training and test sets and write them to
# their respective dictionaries
with db_con:
    for symbol in symbols:

        # select all features and the closing price
        cur = db_con.cursor()
        cur.execute('SELECT {0}_15m.close, {0}_15m_feat.* FROM {0}_15m_feat JOIN {0}_15m ON {0}_15m.t_open={0}_15m_feat.t_open'.format(symbol))
        data = np.array(cur.fetchall()).astype('float32')

        # drop the first n observations (longest period length in feature calculation)
        data = data[100:, :]

        # split data into test and training
        test_split = int(len(data) * TEST_RATIO)

        # create training data
        train_X = data[:test_split, 2:]
        train_y = data[F_HORIZON:F_HORIZON + test_split, 0]

        # create test data
        test_X = data[test_split + 1: len(data) - F_HORIZON - 1, 2:]
        test_y = data[test_split + 1 + F_HORIZON: len(data) - 1, 0]

        # scale data
        scaler = MinMaxScaler()
        train_X = scaler.fit_transform(train_X)
        #train_y = scaler.fit_transform(train_y.reshape(-1, 1))
        train_y = train_y.reshape(-1, 1)
        test_X = scaler.fit_transform(test_X)
        #test_y = scaler.fit_transform(test_y.reshape(-1, 1))
        test_y = test_y.reshape(-1, 1)

        # join training data and make dictionary
        training_data = np.hstack((train_X, train_y))
        training_dict[symbol] = training_data

        # transform test data and make dictionary
        test_X, test_y = transform_fn(test_X, test_y)
        test_dict[symbol] = [test_X, test_y]


# combine training data for all symbols and shuffle
training_data = combine_symbols(training_dict, chunksize=20, batchsize=5, shuffle=True)

# split training data into features and targets
training_data = np.hsplit(training_data, np.array((len(training_data[0])-1, len(training_data[0]))))
train_X = training_data[0]
train_y = training_data[1].flatten()

# transform training data
train_X, train_y = transform_fn(train_X, train_y)


# TRAIN AND EVALUATE MODEL

# train model
for _ in range(0, 5):
    regressor.train(input_fn=lambda: train_input_fn(train_X, train_y, BATCH_SIZE),
                    steps=int(len(train_y) / BATCH_SIZE))


# evaluate model
for symbol in symbols:
    test_X = test_dict[symbol][0]
    test_y = test_dict[symbol][1]

    print('Evaluating {}'.format(symbol))
    regressor.evaluate(input_fn=lambda: train_input_fn(test_X, test_y, BATCH_SIZE),
                       steps=int(len(test_y) / BATCH_SIZE))
