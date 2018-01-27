# LOAD LIBRARIES & FILES

# load libraries
from binance.client import Client
import configparser
import sqlite3

# read credentials
configParser = configparser.ConfigParser()
configParser.read(r'credentials/API-key')

api_key = configParser.get('credentials', 'api_key')
api_sec = configParser.get('credentials', 'api_secret')

# read config
configParser.read(r'config.txt')
db_path = configParser.get('config', 'db_path')



# TEMPORARY
symbol = 'BNBETH'
interval = '15m'
time_start = 'August 14, 2016 CET'



# CREATE TABLE ON DATABASE

# connect to database
db_con = sqlite3.connect(db_path)

# create table if it does not exist yet
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

# set up client
client = Client(api_key, api_sec)


# download data
output = client.get_historical_klines(symbol, interval, time_start)

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
