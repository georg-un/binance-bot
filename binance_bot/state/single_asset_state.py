from typing import List, Union

import pandas as pd

from binance_bot.client.binance_client import BinanceClient
from binance_bot.configs.client_config import ClientConfig
from binance_bot.processing.feature_calculator import FeatureCalculator
from binance_bot.state.abstract_state import AbstractState


class SingleAssetState(AbstractState):

    def __init__(
            self,
            client: BinanceClient,
            client_config: ClientConfig,
            feature_calculator: FeatureCalculator
    ):
        self._client = client
        self._client_config = client_config
        self._feature_calc = feature_calculator

    def next_step(self):
        # get assets
        self.assets = self._client.get_assets(self._client_config.TARGET_SYMBOL)
        # get klines of target pair
        self.klines = self._client.get_klines(self._client_config.TARGET_PAIR, self._client_config.INTERVALS[0])
        # get klines of feature pairs
        feature_pairs: Union[pd.DataFrame, None] = None
        if self._client_config.FEATURE_PAIRS and len(self._client_config.FEATURE_PAIRS) > 0:
            feature_pairs = pd.concat([
                self._client.get_klines(feature_pair, self._client_config.INTERVALS[0])
                for feature_pair in self._client_config.FEATURE_PAIRS
            ])
        # Calculate all features
        self.features = self._feature_calc.calculate_features(self.klines, feature_pairs)
