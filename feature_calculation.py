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

# read momentum incidator config
adx_period = int(configParser.get('momentum', 'adx_period'))
cci_period = int(configParser.get('momentum', 'cci_period'))
rsi_period = int(configParser.get('momentum', 'rsi_period'))

stoch_rsi_period = int(configParser.get('momentum', 'stoch_rsi_period'))
fastk_period = int(configParser.get('momentum', 'fastk_period'))
fastd_period = int(configParser.get('momentum', 'fastd_period'))
fastd_matype = int(configParser.get('momentum', 'fastd_matype'))

macd_fastperiod = int(configParser.get('momentum', 'macd_fastperiod'))
macd_slowperiod = int(configParser.get('momentum', 'macd_slowperiod'))
macd_signalperiod = int(configParser.get('momentum', 'macd_signalperiod'))


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


# MOMENTUM INDICATORS

def get_adx(high_list, low_list, close_list, date_list, adx_period):
    """Calculate ADX given high, low and close values as well as a period-parameter from config.txt. Return a
       2-dimensional numpy array containing the ADX-values and the respective timestamps."""

    # calculate adx
    adx = talib.ADX(high=np.array([i[0] for i in high_list]),
                    low=np.array([i[0] for i in low_list]),
                    close=np.array([i[0] for i in close_list]),
                    timeperiod=adx_period)

    # combine adx-array with timestamps and return it
    adx = np.column_stack((adx, np.array([i[0] for i in date_list])))
    return adx


def get_cci(high_list, low_list, close_list, date_list, cci_period):
    """Calculate CCI given high, low and close values as well as a period-parameter from config.txt. Return a
       2-dimensional numpy array containing the CCI-values and the respective timestamps."""

    # calculate cci
    cci = talib.CCI(high=np.array([i[0] for i in high_list]),
                    low=np.array([i[0] for i in low_list]),
                    close=np.array([i[0] for i in close_list]),
                    timeperiod=cci_period)

    # combine cci-array with timestamps and return it
    cci = np.column_stack((cci, np.array([i[0] for i in date_list])))
    return cci


def get_macd(price_list, date_list, macd_fastperiod, macd_slowperiod, macd_signalperiod):
    """Calculate MACD given price values as well as period-parameters from config.txt. Return a
           4-dimensional numpy array containing the MACD, the Signal, the histogram and the respective timestamps."""
    macd = talib.MACD(np.array([i[0] * 10000 for i in price_list]),
                      fastperiod=macd_fastperiod,
                      slowperiod=macd_slowperiod,
                      signalperiod=macd_signalperiod)

    macd = np.column_stack((macd[0],
                            macd[1],
                            macd[2],
                            np.array([i[0] for i in date_list])))

    return macd


def get_rsi(close_list, date_list, rsi_period):
    """Calculate RSI given only close values as well as a period-parameter from config.txt. Return a
       2-dimensional numpy array containing the RSI-values and the respective timestamps."""

    # calculate rsi
    rsi = talib.RSI(np.array([i[0] * 10000 for i in close_list]),
                    timeperiod=rsi_period)

    # combine rsi-array with timestamps and return it
    rsi = np.column_stack((rsi, np.array([i[0] for i in date_list])))
    return rsi


def get_stoch_rsi(close_list, date_list, stoch_rsi_period, fastk_period, fastd_period, fastd_matype):
    """Calculate Stochastic RSI given only close values as well as parameters from config.txt. Return a
       2-dimensional numpy array containing the Stochastic RSI-values and the respective timestamps."""
    stoch_rsi = talib.STOCHRSI(np.array([i[0] * 10000 for i in close_list]),
                               timeperiod=stoch_rsi_period,
                               fastk_period=fastk_period,
                               fastd_period=fastd_period,
                               fastd_matype=fastd_matype)
    stoch_rsi = np.column_stack((stoch_rsi[0], stoch_rsi[1], np.array([i[0] for i in date_list])))
    return stoch_rsi


# VOLATILITY INDICATORS

def get_bollinger_bands(price_list, date_list, bbands_period, bbands_upper, bbands_lower, bbands_matype):
    """Calculate Bollinger Bands given a price list and parameters from config.txt. Return a 4-dimensional numpy array
    containing the three Bollinger Bands as well as date values.
    Note: price values have to be multiplied before calculations and divided afterwards due to a bug in talib occuring
    with small values (https://github.com/mrjbq7/ta-lib/issues/151)"""

    # calculate bollinger bands
    results_list = talib.BBANDS(price_list * 10000,
                                timeperiod=bbands_period,
                                nbdevup=bbands_upper,
                                nbdevdn=bbands_lower,
                                matype=bbands_matype)

    # divide results by 100000
    bband_up = results_list[0] / 10000
    bband_mid = results_list[1] / 10000
    bband_low = results_list[2] / 10000

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
                            'bband_low DOUBLE, ' +
                            'adx DOUBLE, ' +
                            'cci DOUBLE, ' +
                            'macd DOUBE, ' +
                            'macd_signal DOUBLE, ' +
                            'macd_hist DOUBLE, ' +
                            'rsi DOUBLE, ' +
                            'stoch_rsi_k DOUBLE, ' +
                            'stoch_rsi_d DOUBLE)')

                # copy column t_open to the new table
                cur.execute('INSERT INTO {}_{}_feat (t_open)'.format(symbol, interval) +
                            'SELECT t_open FROM {}_{}'.format(symbol, interval))

                # GET DATA FROM DATABASE
                # get values for high, low, close and time
                cur.execute('SELECT high FROM {}_{}'.format(symbol, interval))
                high_list = cur.fetchall()
                cur.execute('SELECT low FROM {}_{}'.format(symbol, interval))
                low_list = cur.fetchall()
                cur.execute('SELECT close FROM {}_{}'.format(symbol, interval))
                close_list = cur.fetchall()
                cur.execute('SELECT t_open FROM {}_{}'.format(symbol, interval))
                date_list = cur.fetchall()

                # INDICATOR: TYPICAL PRICE
                # calculate the typical price
                typical_price_array = get_typical_price(high_list, low_list, close_list, date_list)

                # write the typical price to the database
                for x in range(0, len(typical_price_array)):
                    cur.execute('UPDATE {}_{}_feat SET price = ? WHERE t_open = ?'.format(symbol, interval),
                                (typical_price_array[x, 0],
                                 int(typical_price_array[x, 1])))

                # MOMENTUM INDICATORS

                # INDICATOR: ADX
                # calculate adx
                adx_array = get_adx(high_list=high_list,
                                    low_list=low_list,
                                    close_list=close_list,
                                    date_list=date_list,
                                    adx_period=adx_period)

                # write adx to database
                for x in range(0, len(adx_array)):
                    cur.execute('UPDATE {}_{}_feat SET adx = ? WHERE t_open = ?'.format(symbol, interval),
                                (adx_array[x, 0],
                                 int(adx_array[x, 1])))

                # INDICATOR: CCI
                # calculate cci
                cci_array = get_cci(high_list=high_list,
                                    low_list=low_list,
                                    close_list=close_list,
                                    date_list=date_list,
                                    cci_period=cci_period)

                # write cci to database
                for x in range(0, len(cci_array)):
                    cur.execute('UPDATE {}_{}_feat SET cci = ? WHERE t_open = ?'.format(symbol, interval),
                                (cci_array[x, 0],
                                 int(cci_array[x, 1])))

                macd_array = get_macd(price_list=close_list,
                                      date_list=date_list,
                                      macd_fastperiod=macd_fastperiod,
                                      macd_slowperiod=macd_slowperiod,
                                      macd_signalperiod=macd_signalperiod)

                # write macd to database
                for x in range(0, len(macd_array)):
                    cur.execute('''UPDATE {}_{}_feat SET macd = ?, macd_signal = ?, 
                    macd_hist = ? WHERE t_open = ?'''.format(symbol, interval),
                                (macd_array[x, 0],
                                 macd_array[x, 1],
                                 macd_array[x, 2],
                                 int(macd_array[x, 3])))

                # INDICATOR: RSI
                # calculate rsi
                rsi_array = get_rsi(close_list=close_list,
                                    date_list=date_list,
                                    rsi_period=rsi_period)

                # write rsi to database
                for x in range(0, len(rsi_array)):
                    cur.execute('UPDATE {}_{}_feat SET rsi = ? WHERE t_open = ?'.format(symbol, interval),
                                (rsi_array[x, 0],
                                 int(rsi_array[x, 1])))

                # INDICATOR: STOCHASTIC RSI
                # calculate stochastic rsi
                stoch_rsi_array = get_stoch_rsi(close_list=close_list,
                                                date_list=date_list,
                                                stoch_rsi_period=stoch_rsi_period,
                                                fastk_period=fastk_period,
                                                fastd_period=fastd_period,
                                                fastd_matype=fastd_matype)

                # write stoch_rsi to database
                for x in range(0, len(stoch_rsi_array)):
                    cur.execute('''UPDATE {}_{}_feat SET stoch_rsi_k = ?, stoch_rsi_d = ? 
                    WHERE t_open = ?'''.format(symbol, interval),
                                (stoch_rsi_array[x, 0],
                                 stoch_rsi_array[x, 1],
                                 int(stoch_rsi_array[x, 2])))


                # VOLATILITY INDICATORS

                # INDICATOR: BOLLINGER BANDS
                # use the reference price according to the setting in config.txt
                if bbands_ref == 'close':
                    bollinger_price = np.array([i[0] for i in close_list])
                else:
                    bollinger_price = typical_price_array[:, 0]

                # calculate bollinger bands
                bollinger_array = get_bollinger_bands(price_list=bollinger_price,
                                                      date_list=date_list,
                                                      bbands_period=bbands_period,
                                                      bbands_upper=bbands_upper,
                                                      bbands_lower=bbands_lower,
                                                      bbands_matype=bbands_matype)

                # write bollinger bands to database
                for x in range(0, len(bollinger_array)):
                    cur.execute('''UPDATE {}_{}_feat SET bband_up = ?, bband_mid = ?, 
                    bband_low = ? WHERE t_open = ?'''.format(symbol, interval),
                                (bollinger_array[x, 0],
                                 bollinger_array[x, 1],
                                 bollinger_array[x, 2],
                                 int(bollinger_array[x, 3])))



