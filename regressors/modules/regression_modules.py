from numpy import array
from tensorflow.contrib.data import Dataset
from tensorflow.python.feature_column import feature_column


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
