# LOAD LIBRARIES & FILES

# load libraries
import configparser
import pathlib
import logging
import sqlite3
import numpy as np
from sklearn.preprocessing import LabelEncoder
from general.general_modules import getlist
from data.prepare.feature_processing import *


# READ CONFIG

# set up config parser
configParser = configparser.ConfigParser()

# read config-file
configParser.read(r'config.txt')

db_path = configParser.get('config', 'db_path')
symbols = getlist(configParser.get('symbols', 'symbol_list'))
intervals = getlist(configParser.get('intervals', 'interval_list'))

# get config for general indicators

# exponential smoothing
exp_smoothing_enabled = configParser.get('general', 'exp_smoothing_enabled') == 'True'
exp_smoothing_alpha = float(configParser.get('general', 'exp_smoothing_alpha'))

# bollinger bands
bbands_period = int(configParser.get('general', 'bbands_period'))
bbands_upper = int(configParser.get('general', 'bbands_upper'))
bbands_lower = int(configParser.get('general', 'bbands_lower'))
bbands_matype = int(configParser.get('general', 'bbands_matype'))
bbands_ref = configParser.get('general', 'bbands_ref')

# ema
ema_period_short = int(configParser.get('general', 'ema_period_short'))
ema_period_mid = int(configParser.get('general', 'ema_period_mid'))
ema_period_long = int(configParser.get('general', 'ema_period_long'))

# sma
sma_period_short = int(configParser.get('general', 'sma_period_short'))
sma_period_mid = int(configParser.get('general', 'sma_period_mid'))
sma_period_long = int(configParser.get('general', 'sma_period_long'))

# get config for momentum indicators

# adx, cci, rsi, roc
adx_period = int(configParser.get('momentum', 'adx_period'))
cci_period = int(configParser.get('momentum', 'cci_period'))
rsi_period = int(configParser.get('momentum', 'rsi_period'))
roc_period = int(configParser.get('momentum', 'roc_period'))

# stochastic rsi
stoch_rsi_period = int(configParser.get('momentum', 'stoch_rsi_period'))
fastk_period = int(configParser.get('momentum', 'fastk_period'))
fastd_period = int(configParser.get('momentum', 'fastd_period'))
fastd_matype = int(configParser.get('momentum', 'fastd_matype'))

# williams %r
will_r_period = int(configParser.get('momentum', 'will_r_period'))

# macd
macd_fastperiod = int(configParser.get('momentum', 'macd_fastperiod'))
macd_slowperiod = int(configParser.get('momentum', 'macd_slowperiod'))
macd_signalperiod = int(configParser.get('momentum', 'macd_signalperiod'))


# SET UP LOGGING

# create log-directory, if it does not already exist yet
pathlib.Path("log/").mkdir(parents=True, exist_ok=True)

# set up log-handler
logger = logging.getLogger('feature_calculation')
log_handler = logging.FileHandler('log/feature_calculation.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)


# SET UP DATABASE CONNECTION

# connect to database
db_con = sqlite3.connect(db_path)


# CALCULATE INDICATORS


# enumerate symbols
symbol_encoder = LabelEncoder()
symbol_encoder.fit(symbols)

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
                            'obv DOUBLE, ' +
                            'symbol int)')

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
                cur.execute('SELECT vol FROM {}_{}'.format(symbol, interval))
                volume_list = cur.fetchall()

                # perform exponential smoothing, if exponential smoothing is enabled in config.txt
                if exp_smoothing_enabled:
                    high_list = exponential_smoothing(input_list=high_list, exp_smoothing_alpha=exp_smoothing_alpha)
                    low_list = exponential_smoothing(input_list=low_list, exp_smoothing_alpha=exp_smoothing_alpha)
                    close_list = exponential_smoothing(input_list=close_list, exp_smoothing_alpha=exp_smoothing_alpha)
                    volume_list = exponential_smoothing(input_list=volume_list, exp_smoothing_alpha=exp_smoothing_alpha)

                # GENERAL INDICATORS

                # INDICATOR: TYPICAL PRICE
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

                # INDICATOR: EMA
                # calculate ema
                ema_array = get_ema(price_list=close_list,
                                    date_list=date_list,
                                    ema_period_short=ema_period_short,
                                    ema_period_mid=ema_period_mid,
                                    ema_period_long=ema_period_long)

                # write ema to database
                for x in range(0, len(ema_array)):
                    cur.execute('''UPDATE {}_{}_feat SET ema_short = ?, ema_mid = ?, 
                    ema_long = ? WHERE t_open = ?'''.format(symbol, interval),
                                (ema_array[x, 0],
                                 ema_array[x, 1],
                                 ema_array[x, 2],
                                 int(ema_array[x, 3])))

                # INDICATOR: SMA
                # calculate sma
                sma_array = get_sma(price_list=close_list,
                                    date_list=date_list,
                                    sma_period_short=sma_period_short,
                                    sma_period_mid=sma_period_mid,
                                    sma_period_long=sma_period_long)

                # write sma to database
                for x in range(0, len(sma_array)):
                    cur.execute('''UPDATE {}_{}_feat SET sma_short = ?, sma_mid = ?, 
                    sma_long = ? WHERE t_open = ?'''.format(symbol, interval),
                                (sma_array[x, 0],
                                 sma_array[x, 1],
                                 sma_array[x, 2],
                                 int(sma_array[x, 3])))

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

                # INDICATOR: ROC
                # calculate roc
                roc_array = get_roc(close_list=close_list,
                                    date_list=date_list,
                                    roc_period=roc_period)

                # write roc to database
                for x in range(0, len(roc_array)):
                    cur.execute('UPDATE {}_{}_feat SET roc = ? WHERE t_open = ?'.format(symbol, interval),
                                (roc_array[x, 0],
                                 int(roc_array[x, 1])))

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

                # INDICATOR: WILLIAMS %R
                # calculate willams %r
                will_r_array = get_will_r(high_list=high_list,
                                          low_list=low_list,
                                          close_list=close_list,
                                          date_list=date_list,
                                          will_r_period=will_r_period)

                # write willams %r to database
                for x in range(0, len(will_r_array)):
                    cur.execute('UPDATE {}_{}_feat SET will_r = ? WHERE t_open = ?'.format(symbol, interval),
                                (will_r_array[x, 0],
                                 int(will_r_array[x, 1])))

                # VOLUME INDICATORS

                # INDICATOR: OBV
                # calculate obv
                obv_array = get_obv(price_list=close_list,
                                    volume_list=volume_list,
                                    date_list=date_list)

                # write obv to database
                for x in range(0, len(obv_array)):
                    cur.execute('UPDATE {}_{}_feat SET obv = ? WHERE t_open = ?'.format(symbol, interval),
                                (obv_array[x, 0],
                                 int(obv_array[x, 1])))

                # SYMBOL ENCONDING
                cur.execute('UPDATE {}_{}_feat SET symbol = {}'.format(symbol, interval,
                                                                       symbol_encoder.transform([symbol])[0]))

                logger.info('Table {}_{}_feat has successfully been created and filled with indicator values.'.format(symbol, interval))

        else:
            logger.warning('Table {}_{}_feat has NOT been created, because it already existed in database.'.format(symbol, interval))
