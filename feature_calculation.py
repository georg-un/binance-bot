# LOAD LIBRARIES & FILES

# load libraries
import configparser
import sqlite3
import talib
import numpy as np


# READ FILES

def getlist(option, sep=',', chars=None):
    """Return a list from a ConfigParser option. By default,
       split on a comma and strip whitespaces."""
    return [ chunk.strip(chars) for chunk in option.split(sep) ]

# set up config parser
configParser = configparser.ConfigParser()

# read config
configParser.read(r'config.txt')

db_path = configParser.get('config', 'db_path')
symbols = getlist(configParser.get('symbols', 'symbol_list'))
intervals = getlist(configParser.get('intervals', 'interval_list'))

# read bollinger bands config
bbands_period = int(configParser.get('bollinger bands', 'bbands_period'))
bbands_upper = int(configParser.get('bollinger bands', 'bbands_upper'))
bbands_lower = int(configParser.get('bollinger bands', 'bbands_lower'))
bbands_matype = int(configParser.get('bollinger bands', 'bbands_matype'))
bbands_ref = configParser.get('bollinger bands', 'bbands_ref')


# SET UP DATABASE CONNECTION

# connect to database
db_con = sqlite3.connect(db_path)


# INDICATOR FUNCTIONS


def get_typical_price(high_list, low_list, close_list, date_list):
    """Take price-lists for high, low and close and calculate (high + low + close) / 3 to get
    the typical price of a period. Return a two dimensional numpy-array containing the typical price values
    as well as date values."""

    # initialize array
    price_array = np.array([], dtype='double')

    # calculate (high + low + close) / 3 for each row
    for element in range(0, len(close_list)):
        typical_price = (high_list[element][0] +
                         low_list[element][0] +
                         close_list[element][0]) / 3

        price_array = np.append(price_array, typical_price)

    # get date array
    date_array = np.array([i[0] for i in date_list])

    # add both arrays to a 2-dimensional array
    typ_price_array = np.column_stack((price_array, date_array))

    return typ_price_array


def get_bollinger_bands(price_list, date_list, bbands_period, bbands_upper, bbands_lower, bbands_matype):
    """Calculate Bollinger Bands given a price list and parameters from config.txt. Return a 4-dimensional numpy array
    containing the three Bollinger Bands as well as date values.
    Note: price values have to be multiplied before calculations and divided afterwards due to a bug in talib occuring
    with small values (https://github.com/mrjbq7/ta-lib/issues/151)"""

    # calculate bollinger bands
    results_list = talib.BBANDS(price_list * 100000,
                                timeperiod=bbands_period,
                                nbdevup=bbands_upper,
                                nbdevdn=bbands_lower,
                                matype=bbands_matype)

    # divide results by 100000
    bband_up = results_list[0] / 100000
    bband_mid = results_list[1] / 100000
    bband_low = results_list[2] / 100000

    # construct 4d-array and return it
    bollinger_array = np.column_stack((bband_up, bband_mid, bband_low, date_list))
    return bollinger_array


# CALCULATE INDICATORS
# Create a table for indicators for every combination of symbols and intervals (foreign key is t_open).
# Subsequently, calculate all indicators and write them to the new table.
for symbol in symbols:
    for interval in intervals:

        # check if table already exists
        with db_con:
            cur = db_con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}_{}_feat'".format(symbol,
                                                                                                         interval))
            if cur.fetchone() is None:
                table_exists = False
            else:
                table_exists = True

        # if table does not exist yet, create it and calculate all indicators
        if not table_exists:
            with db_con:
                cur = db_con.cursor()

                # create table
                cur.execute('CREATE TABLE {}_{}_feat('.format(symbol, interval) +
                            't_open DATETIME, ' +
                            'price DOUBLE, ' +
                            'bband_up DOUBLE, ' +
                            'bband_mid DOUBLE, ' +
                            'bband_low DOUBLE)')

                # copy column t_open to the new table
                cur.execute('INSERT INTO {}_{}_feat (t_open)'.format(symbol, interval) +
                            'SELECT t_open FROM {}_{}'.format(symbol, interval))

                # INDICATOR: TYPICAL PRICE
                # get price values
                cur.execute('SELECT high FROM {}_{}'.format(symbol, interval))
                high_list = cur.fetchall()
                cur.execute('SELECT low FROM {}_{}'.format(symbol, interval))
                low_list = cur.fetchall()
                cur.execute('SELECT close FROM {}_{}'.format(symbol, interval))
                close_list = cur.fetchall()
                cur.execute('SELECT t_open FROM {}_{}'.format(symbol, interval))
                date_list = cur.fetchall()

                # calculate the typical price
                typical_price_array = get_typical_price(high_list, low_list, close_list, date_list)

                # write the typical price to the database
                for x in range(0, len(typical_price_array)):
                    cur.execute('UPDATE {}_{}_feat SET price = ? WHERE t_open = ?'.format(symbol, interval),
                                (typical_price_array[x, 0],
                                 int(typical_price_array[x, 1])))

                # INDICATOR: BOLLINGER BANDS
                # use the reference price according to the setting in config.txt
                if bbands_ref == 'close':
                    bollinger_price = np.array([i[0] for i in close_list])
                else:
                    bollinger_price = typical_price_array[:, 0]

                # calculate bollinger bands
                bollinger_array = get_bollinger_bands(bollinger_price,
                                                      date_list,
                                                      bbands_period,
                                                      bbands_upper,
                                                      bbands_lower,
                                                      bbands_matype)

                # write bollinger bands to database
                for x in range(0, len(bollinger_array)):
                    cur.execute('''UPDATE {}_{}_feat SET bband_up = ?, bband_mid = ?, 
                    bband_low = ? WHERE t_open = ?'''.format(symbol, interval),
                                (bollinger_array[x, 0],
                                 bollinger_array[x, 1],
                                 bollinger_array[x, 2],
                                 int(bollinger_array[x, 3])))
