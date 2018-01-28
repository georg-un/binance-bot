# LOAD LIBRARIES & FILES

# load libraries
from binance.client import Client
import configparser
import sqlite3
import datetime as d


# load functions
def getlist(option, sep=',', chars=None):
    """Return a list from a ConfigParser option. By default,
       split on a comma and strip whitespaces."""
    return [ chunk.strip(chars) for chunk in option.split(sep) ]

def api_time_format(milliseconds):
    """Convert a unix timestamp in milliseconds to the
    date-format required by binance.client."""
    timestamp = d.datetime.fromtimestamp(milliseconds/1000)
    time_str = d.date.strftime(timestamp, '%B %d, %Y %H:%M:%S')
    return time_str


# READ FILES

# read credentials
configParser = configparser.ConfigParser()
configParser.read(r'credentials/API-key')

api_key = configParser.get('credentials', 'api_key')
api_sec = configParser.get('credentials', 'api_secret')


# read config
configParser.read(r'config.txt')

db_path = configParser.get('config', 'db_path')
symbols = getlist(configParser.get('symbols', 'symbol_list'))
intervals = getlist(configParser.get('intervals', 'interval_list'))
time_start = configParser.get('time', 'time_start')
time_end = configParser.get('time', 'time_end')


# create timestamps for beginning and now
if time_start == 'beginning':
    time_start = 946684800000   # January 1, 2000

if time_end == 'now':
    time_end = d.datetime.now().timestamp() * 1000


# SET UP DATABASE CONNECTION AND BINANCE CLIENT

# connect to database
db_con = sqlite3.connect(db_path)

# set up binance client
client = Client(api_key, api_sec)


# Loop over every symbol and over every time-interval. Create for each combination a table in the database,
# if it does not exist yet and fill it with the respective values
for symbol in symbols:
    for interval in intervals:
        # create table in database if it does not exist yet
        with db_con:
            cur = db_con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS {}_{}('.format(symbol, interval) +
                        't_open DATETIME, ' +
                        'open FLOAT, ' +
                        'high FLOAT, ' +
                        'low FLOAT, ' +
                        'close FLOAT, ' +
                        'vol FLOAT, ' +
                        't_close DATETIME, ' +
                        'u_vol FLOAT, ' +
                        'no_trds INT, ' +
                        'tbBav FLOAT, ' +
                        'tbQav FLOAT)')

        # test if there are already entries in the table
        with db_con:
            cur = db_con.cursor()
            cur.execute('SELECT COUNT(*) FROM {}_{}'.format(symbol, interval))
            table_empty = (cur.fetchone()[0] == 0)

        # if there were no entries in the table, get the first time the symbol was traded on binance.com
        if table_empty == True:
            next_db_entry = client.get_historical_klines(symbol = symbol,
                                                         interval = interval,
                                                         start_str = api_time_format(time_start))[0][0]
        # if the table did exist, get the latest entry in the database for the current symbol
        elif table_empty == False:
            with db_con:
                cur = db_con.cursor()
                next_db_entry = cur.execute('SELECT MAX(t_open) FROM {}_{}'.format(symbol, interval)).fetchone()[0]
                next_db_entry += 900000

        # request data on binance, until the database is up to date
        while next_db_entry <= time_end:
            # download data
            output = client.get_historical_klines(symbol = symbol,
                                                  interval = interval,
                                                  start_str = api_time_format(next_db_entry))
            # write downloaded data to database
            with db_con:
                cur = db_con.cursor()
                for x in range(0, len(output)):
                    cur.execute('INSERT INTO {}_{} '.format(symbol, interval) +
                                'VALUES({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})'.format(output[x][0],
                                                                                            output[x][1],
                                                                                            output[x][2],
                                                                                            output[x][3],
                                                                                            output[x][4],
                                                                                            output[x][5],
                                                                                            output[x][6],
                                                                                            output[x][7],
                                                                                            output[x][8],
                                                                                            output[x][9],
                                                                                            output[x][10]))
            # get latest database entry
            with db_con:
                cur = db_con.cursor()
                next_db_entry = cur.execute('SELECT MAX(t_open) FROM {}_{}'.format(symbol, interval)).fetchone()[0]
                next_db_entry += 900000
            print(api_time_format(next_db_entry))


        # wait, until there were on average 1200 requests per minute
        #import time
        #import math
        #minutes = math.ceil(len(output) / 1200)
        #time.sleep(minutes * 60)
