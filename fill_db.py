from typing import List, Dict

from binance_bot.client.binance_client import BinanceClient
from binance_bot.client.database_client import *
from binance_bot.configs.credentials import Credentials
from binance_bot.configs.main_config import MainConfig


def trim_dfs_to_same_length(dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    # set timestamp as index
    [value.set_index(KlineProps.TIME_OPEN, inplace=True) for _, value in dfs.items()]
    # perform an inner join on all dataframes
    joined_df = list(dfs.values())[0]
    for key, value in dfs.items():
        joined_df = joined_df.join(value, how="inner", rsuffix=key)
    # use the length of the joined dataframe to determine the min and max index
    min_timestamp = joined_df.index.min()
    max_timestamp = joined_df.index.max()
    for key, value in dfs.items():
        dfs[key] = value.loc[min_timestamp: max_timestamp]
    # set timestamp as column again
    [value.reset_index(inplace=True) for _, value in dfs.items()]
    return dfs


main_config = MainConfig()
binance_client = BinanceClient(Credentials())
database_client = DatabaseClient(database_config=main_config.DATABASE_CONFIG)

# Set up an empty database
database_client.open_database_connection(recreate_db=True)
# For each pair, download the data, create a table, and insert the values into it
pairs = [main_config.TARGET_PAIR] + main_config.FEATURE_PAIRS
# Download all data
pair_data: Dict[str, pd.DataFrame] = {}
for pair in pairs:
    pair_data[pair] = binance_client.get_historical_data(pair=pair, interval=main_config.INTERVALS[0])
# Trim dataframes to same length
pair_data = trim_dfs_to_same_length(pair_data)
# Write to DB
for pair, data in pair_data.items():
    database_client.create_klines_table(pair=pair)
    database_client.insert_klines_into_table(pair=pair, data=data)
database_client.close_database_connection()
