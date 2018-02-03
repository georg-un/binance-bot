# LOAD LIBRARIES & FILES

# load libraries
import configparser
import sqlite3
import numpy as np
import pandas as pd
import xgboost as xgb


# READ CONFIG

def getlist(option, sep=',', chars=None):
    """Return a list from a ConfigParser option. By default,
       split on a comma and strip whitespaces."""
    return [chunk.strip(chars) for chunk in option.split(sep)]


# set up config parser
configParser = configparser.ConfigParser()

# read config-file
configParser.read(r'config.txt')

db_path = configParser.get('config', 'db_path')
symbols = getlist(configParser.get('symbols', 'symbol_list'))
intervals = getlist(configParser.get('intervals', 'interval_list'))


# SET UP DATABASE CONNECTION

# connect to database
db_con = sqlite3.connect(db_path)


#with db_con:
#    cur = db_con.cursor()
#    cur.execute('SELECT * FROM ADAETH_15m_feat')
#    test = cur.fetchall()


with db_con:
    cur = db_con.cursor()
    cur.execute('SELECT ADAETH_15m.close, ADAETH_15m_feat.* FROM ADAETH_15m_feat JOIN ADAETH_15m ON ADAETH_15m.t_open=ADAETH_15m_feat.t_open')
    data = cur.fetchall()


data = pd.DataFrame(data)
data = data.values


nrow = data.shape[0]
ncol = data.shape[1]
train = data[0:2*(int(nrow/3)), :]
test = data[2*(int(nrow/3)):(nrow-1), :]


X_train = train[:, 1:(train.shape[1]-1)]
y_train = train[:, 0]
X_test = test[:, 1:(test.shape[1]-1)]
y_test = test[:, 0]


model = xgb.XGBClassifier()
model.fit(X_train, y_train)