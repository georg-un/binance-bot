import tensorflow as tf
import tensorflow.contrib.rnn as rnn


def lstm_model(features, labels, mode, params):

    # create input tensor with features
    input_layer = tf.feature_column.input_layer(features, params['feature_columns'])
    input_layer = tf.reshape(tensor=input_layer,
                             shape=[-1, params['batch_size'], 1])

    # reshape lable tensor
    targets = tf.reshape(tensor=labels,
                         shape=[-1, params['batch_size'], 1])

    # create LSTM cells
    first_cell = rnn.BasicLSTMCell(num_units=64, activation=tf.nn.relu)
    second_cell = rnn.BasicLSTMCell(num_units=32, activation=tf.nn.relu)
    third_cell = rnn.BasicLSTMCell(num_units=16, activation=tf.nn.relu)

    # put LSTM cells together
    multi_cell = tf.nn.rnn_cell.MultiRNNCell([first_cell, second_cell, third_cell], state_is_tuple=True)
    rnn_output, states = tf.nn.dynamic_rnn(multi_cell, input_layer, dtype=tf.float32)

    # dense outputs
    stacked_rnn_output = tf.reshape(rnn_output, [-1, 16])
    stacked_outputs = tf.layers.dense(stacked_rnn_output, 1)
    outputs = tf.reshape(stacked_outputs, [-1, params['batch_size'], 1])

    # prediction operation
    if mode == tf.estimator.ModeKeys.PREDICT:
        predictions = {
            'price': outputs
        }
        return tf.estimator.EstimatorSpec(mode, predictions=predictions)

    # evaluation operation
    loss = tf.reduce_sum(tf.square(outputs - targets))

    mae = tf.metrics.mean_absolute_error(targets, outputs, name='mean_absolute_error')
    mse = tf.metrics.mean_squared_error(targets, outputs, name='mean_squared_error')
    rmse = tf.metrics.root_mean_squared_error(targets, outputs, name='root_mean_squared_error')
    #mre = tf.metrics.mean_relative_error(targets, outputs, targets, name='mean_relative_error')

    metrics = {'mean_absolute_error': mae}

    tf.summary.scalar('mean_absolute_error', mae[1])
    tf.summary.scalar('mean_squared_error', mse[1])
    tf.summary.scalar('root_mean_squared_error', rmse[1])
    #tf.summary.scalar('mean_relative_error', mre[1])
    tf.summary.merge_all()

    if mode == tf.estimator.ModeKeys.EVAL:
        return tf.estimator.EstimatorSpec(
            mode, loss=loss, eval_metric_ops=metrics)

    # training operation
    assert mode == tf.estimator.ModeKeys.TRAIN

    optimizer = tf.train.AdamOptimizer(learning_rate=params['learning_rate'])
    train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)