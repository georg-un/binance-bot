# LOAD LIBRARIES
import configparser
import sqlite3
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import pandas as pd
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error


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
        data = cur.fetchall()







# Configuration for RNN
class RNNConfig():
    input_size=1
    num_steps=30
    lstm_size=128
    num_layers=1
    keep_prob=0.8
    batch_size = 64
    init_learning_rate = 0.001
    learning_rate_decay = 0.99
    init_epoch = 5
    max_epoch = 50
    # special for RNN:
    embedding_size = 3
    stock_count = 50

config = RNNConfig()



tf.reset_default_graph()
lstm_graph = tf.Graph()


with lstm_graph.as_default():
    # Dimension = (
    #     number of data examples,
    #     number of input in one computation step,
    #     number of numbers in one input
    # )
    # We don't know the number of examples beforehand, so it is None.
    inputs = tf.placeholder(tf.float32, [None, config.num_steps, config.input_size])
    targets = tf.placeholder(tf.float32, [None, config.input_size])
    learning_rate = tf.placeholder(tf.float32, None)
    # Mapped to an integer. one label refers to one stock symbol.
    stock_labels = tf.placeholder(tf.int32, [None, 1])