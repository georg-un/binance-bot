from binance_bot.client.binance_client import BinanceClient
from binance_bot.client.database_client import *
from binance_bot.configs.credentials import Credentials
from binance_bot.configs.main_config import MainConfig

main_config = MainConfig()
binance_client = BinanceClient(Credentials())
database_client = DatabaseClient(database_config=main_config.DATABASE_CONFIG)

# Set up an empty database
database_client.open_database_connection(recreate_db=True)
# For each pair, download the data, create a table, and insert the values into it
pairs = [main_config.TARGET_PAIR] + main_config.FEATURE_PAIRS
for pair in pairs:
    data = binance_client.get_historical_data(pair=pair, interval=main_config.INTERVALS[0])
    database_client.create_klines_table(pair=pair)
    database_client.insert_klines_into_table(pair=pair, data=data)
database_client.close_database_connection()
