
from __future__ import print_function, division
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

import pandas as pd
import configparser
import sqlite3
import tensorflow.contrib.rnn as rnn




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

# fix random number seed
np.random.seed(7)


# SET UP DATABASE CONNECTION

# connect to database
db_con = sqlite3.connect(db_path)


with db_con:
    for symbol in symbols:
        cur = db_con.cursor()
        cur.execute('SELECT {0}_15m.close, {0}_15m_feat.* FROM {0}_15m_feat JOIN {0}_15m ON {0}_15m.t_open={0}_15m_feat.t_open'.format(symbol))
        data = np.array(cur.fetchall())


"""
't_open DATETIME, ' +
'price DOUBLE, ' +
'bband_up DOUBLE, ' +
'bband_mid DOUBLE, ' +
'bband_low DOUBLE, ' +
                            'ema_short, ' +
                            'ema_mid, ' +
                            'ema_long, ' +
                            'sma_short, ' +
                            'sma_mid, ' +
                            'sma_long, ' +
                            'adx DOUBLE, ' +
                            'cci DOUBLE, ' +
                            'macd DOUBE, ' +
                            'macd_signal DOUBLE, ' +
                            'macd_hist DOUBLE, ' +
                            'rsi DOUBLE, ' +
                            'roc DOUBLE, ' +
                            'stoch_rsi_k DOUBLE, ' +
                            'stoch_rsi_d DOUBLE, ' +
                            'will_r DOUBLE, ' +
                            'obv DOUBLE)"""




# shape inputs
def input_fn(dataset):
    features = {'bband_up': np.array(dataset[100:, 3]).astype('float32'),
                'bband_mid': np.array(dataset[100:, 4]).astype('float32'),
                'bband_low': np.array(dataset[100:, 5]).astype('float32')}
    lables = np.array(dataset[100:, 0]).astype('float32')
    return features, lables


train_X, train_y = input_fn(data)


# input function
def train_input_fn(features, labels, batch_size):
    """An input function for training"""
    # Convert the inputs to a Dataset.
    dataset_ = tf.data.Dataset.from_tensor_slices((dict(features), labels))

    # Shuffle, repeat, and batch the examples.
    dataset_ = dataset_.batch(batch_size)

    # Build the Iterator, and return the read end of the pipeline.
    return dataset_.make_one_shot_iterator().get_next()


# Feature columns describe how to use the input.
my_feature_columns = []
for key in train_X.keys():
    my_feature_columns.append(tf.feature_column.numeric_column(key=key))


model = tf.estimator.DNNRegressor(hidden_units=[9, 9],
                                  feature_columns=my_feature_columns,
                                  model_dir='/home/georg/test/')

#model = tf.estimator.LinearRegressor(feature_columns=my_feature_columns)


model.train(input_fn=lambda: train_input_fn(train_X, train_y, 500), steps=5)


