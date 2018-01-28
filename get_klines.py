# LOAD LIBRARIES & FILES

# load libraries
from binance.client import Client
import configparser
import sqlite3
import datetime as d


# read credentials
configParser = configparser.ConfigParser()
configParser.read(r'credentials/API-key')

api_key = configParser.get('credentials', 'api_key')
api_sec = configParser.get('credentials', 'api_secret')

# read config
configParser.read(r'config.txt')
db_path = configParser.get('config', 'db_path')



# TEMPORARY
symbol = 'LTCETH'
interval = '15m'
time_start = 'October 14, 2004 CET'
time_end = d.datetime.now().utcnow().timestamp() * 1000



def api_time_format(milliseconds):
    timestamp = d.datetime.fromtimestamp(milliseconds/1000)
    time_str = d.date.strftime(timestamp, '%B %d, %Y %H:%M:%S')
    return time_str



# connect to database
db_con = sqlite3.connect(db_path)

# set up client
client = Client(api_key, api_sec)






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


# test if there are already entries in the table
with db_con:
    cur = db_con.cursor()
    cur.execute('SELECT COUNT(*) FROM {}_{}'.format(symbol, interval))
    table_empty = (cur.fetchone()[0] == 0)


# if there were no entries in the table, get the first time the symbol was traded on binance.com
if table_empty == True:
    start_time = client.get_historical_klines(symbol=symbol,
                                              interval=interval,
                                              start_str=time_start)[0][0]
# if the table did exist, get the latest entry in the database for the current symbol
elif table_empty == False:
    with db_con:
        cur = db_con.cursor()
        start_time = cur.execute('SELECT MAX(t_open) FROM {}_{}'.format(symbol, interval)).fetchone()[0]








# most_recent = start_time
# so lange most_recent < als end_time, hol daten und schreibe in datenbank
# errechne neuen most_recent

most_recent = start_time

while most_recent <= time_end:
    # download data
    output = client.get_historical_klines(symbol = symbol,
                                          interval = interval,
                                          start_str = api_time_format(most_recent))
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
        most_recent = cur.execute('SELECT MAX(t_open) FROM {}_{}'.format(symbol, interval)).fetchone()[0]






#import datetime
#dates = [lst[0] for lst in output]
#print([datetime.datetime.fromtimestamp(x/1000) for x in dates])

