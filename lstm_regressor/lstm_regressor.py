import numpy as np
import tensorflow as tf
import tensorflow.contrib.rnn as rnn
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import configparser
import sqlite3


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

#data = data[100:150, :]

##########################################

batch_size = 200
f_horizon = 1

data_X = data[100:100+batch_size, 2:]
test_X = data[100+batch_size+1:100+batch_size+100, 2:]
data_y = data[100+f_horizon:100+batch_size+f_horizon, 0]


scaler = MinMaxScaler()
data_X = scaler.fit_transform(data_X)
test_X = scaler.fit_transform(test_X)




x_batches = data_X.reshape(-1, batch_size, 1)
y_batches = data_y.reshape(-1, batch_size, 1)


tf.reset_default_graph()

X = tf.placeholder(tf.float32, [None, batch_size, 1])
y = tf.placeholder(tf.float32, [None, batch_size, 1])


first_cell = rnn.BasicLSTMCell(num_units=64, activation=tf.nn.relu)
second_cell = rnn.BasicLSTMCell(num_units=32, activation=tf.nn.relu)
third_cell = rnn.BasicLSTMCell(num_units=16, activation=tf.nn.relu)

all_cells = tf.nn.rnn_cell.MultiRNNCell([first_cell, second_cell, third_cell], state_is_tuple=True)
rnn_output, states = tf.nn.dynamic_rnn(all_cells, X, dtype=tf.float32)


stacked_rnn_output = tf.reshape(rnn_output, [-1, 16])
stacked_outputs = tf.layers.dense(stacked_rnn_output, 1)
outputs = tf.reshape(stacked_outputs, [-1, batch_size, 1])

loss = tf.reduce_sum(tf.square(outputs - y))
optimizer = tf.train.AdamOptimizer(learning_rate=0.00001)
training_op = optimizer.minimize(loss)

init = tf.global_variables_initializer()


epochs = 2000

with tf.Session() as sess:
    init.run()
    for ep in range(epochs):
        sess.run(training_op, feed_dict={X: x_batches, y: y_batches})
        if ep % 100 == 0:
            mse = loss.eval(feed_dict={X: x_batches, y: y_batches})
            print(ep, "\tMSE:", mse)
