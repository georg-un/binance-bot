import configparser
import sqlite3

import numpy as np
import tensorflow as tf

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import r2_score

from general.general_modules import getlist
from regressors.modules.regression_modules import transform_fn
from regressors.modules.regression_modules import train_input_fn
from regressors.modules.regression_modules import get_default_feature_columns
from regressors.modules.regression_modules import combine_symbols
from regressors.modules.regression_modules import get_return


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


# DEFINE MODEL

# define regressor
regressor = tf.estimator.DNNRegressor(hidden_units=[256, 128, 64, 32, 16],
                                      feature_columns=get_default_feature_columns(),
                                      model_dir='/home/georg/test/dnn')


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
        train_y = data[:F_HORIZON + test_split, 0]
        train_y = get_return(train_y, F_HORIZON)

        # create test data
        test_X = data[test_split + 1: len(data) - F_HORIZON, 2:]
        test_y = data[test_split + 1:, 0]
        test_y = get_return(test_y, F_HORIZON)

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


# TRAIN MODEL

# train model
for epoch in range(0, 50):
    print('Training: epoch {}'.format(epoch))
    regressor.train(input_fn=lambda: train_input_fn(train_X, train_y, BATCH_SIZE), steps=int(len(train_y)/BATCH_SIZE))


# EVALUATE MODEL

# use build in evaluation
for symbol in symbols:
    test_X = test_dict[symbol][0]
    test_y = test_dict[symbol][1]

    print('Evaluating {}'.format(symbol))

    regressor.evaluate(input_fn=lambda: train_input_fn(test_X, test_y, BATCH_SIZE))


# get predictions
metrics = {'MAE': [],
           'EVS': [],
           'R2': []}

for symbol in symbols:
    test_X = test_dict[symbol][0]
    test_y = test_dict[symbol][1]

    # get predictions
    predictions = list(regressor.predict(input_fn=lambda: train_input_fn(test_X, test_y, BATCH_SIZE)))
    predict_y = [predictions[i]['predictions'] for i in range(0, len(predictions))]
    predict_y = np.asarray(predict_y).reshape(-1, 1)

    # transform scaled predictions back to normal
    #scaler.fit(test_y)
    #predict_y = scaler.inverse_transform(predict_y)

    # calculate metrics
    metrics['MAE'].append(
        mean_absolute_error(test_y, predict_y))
    metrics['EVS'].append(
        explained_variance_score(test_y, predict_y))
    metrics['R2'].append(
        r2_score(test_y, predict_y))

# print scores
print('Explained Variance Score: Highest={}, Lowest={}, Mean={}'.format(
    max(metrics['EVS']),
    min(metrics['EVS']),
    np.mean(metrics['EVS'])
))
print('Mean Absolute Error: Highest={}, Lowest={}, Mean={}'.format(
    max(metrics['MAE']),
    min(metrics['MAE']),
    np.mean(metrics['MAE'])
))
print('R Squared: Highest={}, Lowest={}, Mean={}'.format(
    max(metrics['R2']),
    min(metrics['R2']),
    np.mean(metrics['R2'])
))

import matplotlib.pyplot as plt
plt.plot(test_y)
plt.plot(predict_y)