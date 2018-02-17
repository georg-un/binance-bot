from numpy import array
from tensorflow.contrib.data import Dataset
from tensorflow.python.feature_column import feature_column
import numpy as np


def transform_fn(features, labels):
    """ Transform numpy ndarrays for features and labels from the database
    to the right format for the input function

    Args:
        features: A n-dimensional numpy array containing all the features as listed down below
        labels: A 1-dimensional numpy array containing only the price values for the target period

    Returns:
        features: A dict containing the name of each feature as key and the respective numpy arrays as values
        labels: A 1-dimensional numpy array

    """
    features = {'bband_up': array(features[:, 0]).astype('float32'),
                'bband_mid': array(features[:, 1]).astype('float32'),
                'bband_low': array(features[:, 2]).astype('float32'),
                'ema_short': array(features[:, 3]).astype('float32'),
                'ema_mid': array(features[:, 4]).astype('float32'),
                'ema_long': array(features[:, 5]).astype('float32'),
                'sma_short': array(features[:, 6]).astype('float32'),
                'sma_mid': array(features[:, 7]).astype('float32'),
                'sma_long': array(features[:, 8]).astype('float32'),
                'adx': array(features[:, 9]).astype('float32'),
                'cci': array(features[:, 10]).astype('float32'),
                'macd': array(features[:, 11]).astype('float32'),
                'macd_signal': array(features[:, 12]).astype('float32'),
                'macd_hist': array(features[:, 13]).astype('float32'),
                'rsi': array(features[:, 14]).astype('float32'),
                'roc': array(features[:, 15]).astype('float32'),
                'stoch_rsi_k': array(features[:, 16]).astype('float32'),
                'stoch_rsi_d': array(features[:, 17]).astype('float32'),
                'will_r': array(features[:, 18]).astype('float32'),
                'obv': array(features[:, 19]).astype('float32')}

    labels = array(labels[:]).astype('float32')
    return features, labels


def train_input_fn(features, labels, batch_size):
    """ Input function for training regression models.

    Args:
        features: A dict containing the name of each feature as key and the respective numpy arrays as values
                  (first output of transform_fn)
        labels: A 1-dimensional numpy array containing only the price values for the target period
                (second output of transform_fn)
        batch_size: An integer value for the size of each batch

    Returns:
        Initializes an iterator with a tf.Tensor object that points to the next element


    Example:
        regressor.train(input_fn=lambda: train_input_fn(feature_X, lable_y, 10), steps=100)

    """
    # Convert the inputs to a Dataset.
    dataset_ = Dataset.from_tensor_slices((dict(features), labels))

    # Shuffle, repeat, and batch the examples.
    dataset_ = dataset_.batch(batch_size)

    # Build the Iterator, and return the read end of the pipeline.
    return dataset_.make_one_shot_iterator().get_next()


def get_feature_columns(features):
    """ Create a list of feature colums as required by tf.estimator estimators

    Args: A dict (as created by transform_fn) containing all the features as keys

    Returns: A list of _NumericColumn objects

    """
    feature_columns = []

    for key in features.keys():
        feature_columns.append(feature_column.numeric_column(key=key))

    return feature_columns


def get_default_feature_columns():
    features = {'bband_up': [],
                'bband_mid': [],
                'bband_low': [],
                'ema_short': [],
                'ema_mid': [],
                'ema_long': [],
                'sma_short': [],
                'sma_mid': [],
                'sma_long': [],
                'adx': [],
                'cci': [],
                'macd': [],
                'macd_signal': [],
                'macd_hist': [],
                'rsi': [],
                'roc': [],
                'stoch_rsi_k': [],
                'stoch_rsi_d': [],
                'will_r': [],
                'obv': []}

    feature_columns = []

    for key in features.keys():
        feature_columns.append(feature_column.numeric_column(key=key))

    return feature_columns


def combine_symbols(features_by_symbol, chunksize, batchsize, shuffle=True):
    """
    Args:
        features_by_symbol: A dictionary containing the currency symbols as keys and the feature_dictionaries generated
                            by transform_fn() as values. Its length must be perfectly divisible by chunksize and
                            batchsize, if shuffle is set to True.

        chunksize: An integer value for the size of the chunks which stay togehter when shuffling is applied. Should be
                   set to None if shuffle is set to False.

        batchsize: An integer value for the size of batches which are fed to the machine learning algorithm. Should be
                   set to None if shuffle is set to False.

        shuffle: Logical. Determines if the data should be shuffled in chunks of size chunksize before being returned.

    Returns:
        A numpy array containing all the feature data for all currencies supplied by features_by_symbol

    """

    if shuffle:
        if len(features_by_symbol) % chunksize != 0:
            print('features by symbol (length: {}) is not divisible by the chunksize {} without a remainder'.format(
                len(features_by_symbol),
                chunksize))
            return
        elif len(features_by_symbol) % batchsize != 0:
            print('features by symbol (length: {}) is not divisible by the batchsize {} without a remainder'.format(
                len(features_by_symbol),
                batchsize))
            return

    # combine datasets
    dataset = array([]).astype('float32')

    for key in features_by_symbol:
        np.append(dataset, features_by_symbol[key])

    if shuffle:
        # change dimension of array to shuffle in chunks
        dataset = dataset.reshape(-1, chunksize)

        # shuffle dataset
        np.random.shuffle(dataset)

        # flatten dataset to a 1 dimensional array
        dataset = dataset.flatten()

    # return whole numpy array
    return dataset
