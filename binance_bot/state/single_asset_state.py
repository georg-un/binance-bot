from typing import List, Union

import pandas as pd

from binance_bot.client.binance_client import BinanceClient
from binance_bot.configs.main_config import MainConfig
from binance_bot.processing.feature_calculator import FeatureCalculator
from binance_bot.state.abstract_state import AbstractState


class SingleAssetState(AbstractState):

    def __init__(
            self,
            client: BinanceClient,
            main_config: MainConfig,
            feature_calculator: FeatureCalculator
    ):
        self._client = client
        self._client_config = main_config
        self._feature_calc = feature_calculator

    def next_step(self):
        # get assets
        self.assets = self._client.get_assets([self._client_config.TARGET_SYMBOL, self._client_config.BASE_SYMBOL])
        # get klines of target pair
        self.klines = self._client.get_klines(self._client_config.TARGET_PAIR, self._client_config.INTERVALS[0])
        # get klines of feature pairs
        feature_pairs: Union[pd.DataFrame, None] = None
        if self._client_config.FEATURE_PAIRS and len(self._client_config.FEATURE_PAIRS) > 0:
            for pair in self._client_config.FEATURE_PAIRS:
                pair_klines = self._client.get_klines(pair, self._client_config.INTERVALS[0])
                pair_klines = pair_klines.add_prefix(pair + '_')
                feature_pairs = pd.concat([feature_pairs, pair_klines], axis=1)
                print(feature_pairs)
        # Calculate all features
        self.features = self._feature_calc.calculate_features(self.klines, feature_pairs)
