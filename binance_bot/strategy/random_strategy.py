import random
from typing import List

import pandas as pd

from binance_bot.configs.main_config import MainConfig
from binance_bot.constants import AssetProps, KlineProps
from binance_bot.strategy.abstract_strategy import AbstractStrategy
from binance_bot.strategy.strategy_action import StrategyAction


class RandomStrategy(AbstractStrategy):

    def __init__(self, main_config: MainConfig):
        self._config = main_config

    def apply(
            self,
            klines: pd.DataFrame,
            features: pd.DataFrame,
            assets: pd.DataFrame
    ) -> StrategyAction:
        target_symbol_asset = assets.loc[assets[AssetProps.ASSET] == self._config.TARGET_SYMBOL]
        base_symbol_asset = assets.loc[assets[AssetProps.ASSET] == self._config.BASE_SYMBOL]
        max_sellable_qty = target_symbol_asset[AssetProps.FREE].iloc[0]
        max_buyable_qty = klines[KlineProps.CLOSE].iloc[-1] * base_symbol_asset[AssetProps.FREE].iloc[0]
        if random.choice([True, False, False]):
            return StrategyAction(
                side="SELL",
                pair=self._config.TARGET_PAIR,
                quantity=random.uniform(0, max_sellable_qty)
            )
        if random.choice([True, False]):
            return StrategyAction(
                side="BUY",
                pair=self._config.TARGET_PAIR,
                quantity=random.uniform(0, max_buyable_qty)
            )
