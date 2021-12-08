import pandas as pd

from binance_bot.client.binance_client import BinanceClient
from binance_bot.configs.client_config import ClientConfig
from binance_bot.processing.feature_calculator import FeatureCalculator
from binance_bot.state.abstract_state import AbstractState


class DefaultState(AbstractState):

    def __init__(
            self,
            binance_client: BinanceClient,
            client_config: ClientConfig,
            feature_calculator: FeatureCalculator
    ):
        self._client = binance_client
        self._client_config = client_config
        self._feature_calc = feature_calculator

    def next_step(self):
        self.klines = self._client.get_klines(self._client_config.PAIRS[0], self._client_config.INTERVALS[0])
        self.features = self._feature_calc.calculate_features(self.klines)
        self.open_orders = self._client.get_open_orders()
        self.assets = self._client.get_assets(self._client_config.SYMBOLS)
