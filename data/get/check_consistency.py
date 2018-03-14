# LOAD LIBRARIES & FILES

# load libraries
from binance.client import interval_to_milliseconds
import configparser
import sqlite3
import pathlib
import logging


# load functions
def getlist(option, sep=',', chars=None):
    """Return a list from a ConfigParser option. By default,
       split on a comma and strip whitespaces."""
    return [ chunk.strip(chars) for chunk in option.split(sep) ]


# READ FILES

# set up config parser
configParser = configparser.ConfigParser()

# read config
configParser.read(r'config.txt')

db_path = configParser.get('config', 'db_path')
verbose = configParser.get('config', 'verbose')
symbols = getlist(configParser.get('symbols', 'symbol_list'))
intervals = getlist(configParser.get('intervals', 'interval_list'))


# SET UP LOGGING

# create log-directory, if it does not already exist yet
pathlib.Path("log/").mkdir(parents=True, exist_ok=True)

# set up log-handler
logger = logging.getLogger('check_consistency')
log_handler = logging.FileHandler('log/check_constistency.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)


# SET UP DATABASE CONNECTION

# connect to database
db_con = sqlite3.connect(db_path)


# DEFINE FUNCTIONS FOR CONSISTENCY CHECKS

def check_time_column (symbol_str, interval_str, time_col_str, database_connection):
    """Check the differences between the rows in the database which contain timestamps. Write a warning
    to the log file, if a difference is higher or lower than the selected time-interval"""

    # Get all values of the column from the database
    with database_connection:
        cursor = database_connection.cursor()
        cursor.execute('SELECT {} FROM {}_{}'.format(time_col_str,
                                                     symbol_str,
                                                     interval_str))
        time_col_array = cursor.fetchall()

    # Compare the difference between each two rows to the selected interval. Write a warning to the log file, if
    # there are discrepancies
    for index in range(1, len(time_col_array)):
        time_difference = time_col_array[index][0] - time_col_array[index - 1][0]
        time_interval = interval_to_milliseconds(interval_str)
        if time_difference != time_interval:
            logger.warning(
                'Table {}_{}, column {}, index {}: Inconsistent time interval (difference = {} seconds)'.format(
                    symbol_str,
                    interval_str,
                    time_col_str,
                    index,
                    (time_difference - time_interval) / 1000
                )
            )
    return


def check_if_column_null (symbol_str, interval_str, null_col_str, database_connection):
    """Check if any row in a price column contains a NULL value. If it contains a NULL value,
    write its index to the logfile."""

    # Get all values of the column from the database
    with database_connection:
        cursor = database_connection.cursor()
        cursor.execute('SELECT * FROM {}_{} WHERE {} IS NULL'.format(symbol_str,
                                                                     interval_str,
                                                                     null_col_str)
                       )

        null_col_array = cursor.fetchall()

    # If there were entries with NULL-values, write their index to the logfile
    if len(null_col_array) > 0:
        for index in range(0,len(null_col_array)):
            logger.warning('Table {}_{}, column {}, index {}: Value is NULL'.format(symbol_str,
                                                                                    interval_str,
                                                                                    null_col_str,
                                                                                    index)
                           )

    return


# RUN CONSISTENCY CHECKS

# define column names
time_columns = ('t_open', 't_close')
null_columns = ('t_open', 't_close', 'open', 'high', 'low', 'close',
                'vol', 'u_vol', 'no_trds', 'tbBav', 'tbQav')

# For each combination of symbol and interval, run a check for NULL values and run a check for
# inconsistent time intervals
for symbol in symbols:
    for interval in intervals:
        for null_column in null_columns:
            check_if_column_null(symbol, interval, null_column, db_con)

        for time_column in time_columns:
            check_time_column(symbol, interval, time_column, db_con)


logger.info('All consistency checks have been executed.')
