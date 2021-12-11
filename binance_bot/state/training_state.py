import random
from typing import List, Union

import pandas as pd

from binance_bot.client.binance_client import BinanceClient
from binance_bot.client.database_client import DatabaseClient
from binance_bot.configs.main_config import MainConfig
from binance_bot.constants import AssetProps
from binance_bot.processing.feature_calculator import FeatureCalculator
from binance_bot.state.abstract_state import AbstractState


class TrainingState(AbstractState):

    BATCH_SIZE = 500
    _start_index = None
    _end_index = None

    def __init__(
            self,
            main_config: MainConfig,
            feature_calculator: FeatureCalculator
    ):
        self._main_config = main_config
        self._feature_calc = feature_calculator
        # Get tables from database
        client = DatabaseClient(database_config=main_config.DATABASE_CONFIG)
        client.open_database_connection()
        self._target_pair_table = client.read_table(self._main_config.TARGET_PAIR)
        self._feature_pair_tables = {}
        for pair in self._main_config.FEATURE_PAIRS:
            self._feature_pair_tables[pair] = client.read_table(pair)
        client.close_database_connection()

    def next_batch(self) -> None:
        self.assets = self._generate_random_assets()
        last_possible_start_index = self._target_pair_table.shape[0] - self.BATCH_SIZE
        self._start_index = random.randint(0, last_possible_start_index)
        self._end_index = self._start_index + self.BATCH_SIZE

    def next_step(self) -> None:
        # get klines of target pair
        self.klines = self._target_pair_table.iloc[self._start_index: self._end_index]
        # get klines of feature pairs
        feature_pairs: Union[pd.DataFrame, None] = None
        for pair, data in self._feature_pair_tables.items():
            pair_klines = data.iloc[self._start_index, self._end_index]
            pair_klines = pair_klines.add_prefix(pair + '_')
            feature_pairs = pd.concat([feature_pairs, pair_klines], axis=1)
        # Calculate all features
        self.features = self._feature_calc.calculate_features(self.klines, feature_pairs)
        # Increase indices by 1
        self._start_index += 1
        self._end_index += 1

    def _generate_random_assets(self) -> pd.DataFrame:
        target_symbol_asset = {
            [AssetProps.ASSET]: self._main_config.TARGET_SYMBOL,
            [AssetProps.LOCKED]: 0,
            [AssetProps.FREE]: 0
        }
        base_symbol_asset = {
            [AssetProps.ASSET]: self._main_config.BASE_SYMBOL,
            [AssetProps.LOCKED]: 0,
            [AssetProps.FREE]: random.randint(1, 10000)
        }
        return pd.DataFrame([target_symbol_asset, base_symbol_asset])
