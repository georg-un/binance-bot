import random
from typing import List

import pandas as pd

from binance_bot.configs.main_config import MainConfig
from binance_bot.constants import AssetProps
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
    ) -> List[StrategyAction]:
        actions: List[StrategyAction] = []
        # randomly buy something
        if random.choice([True, True, False]):
            actions.append(
                StrategyAction(side="BUY", pair=self._config.TARGET_PAIR, quantity=1.0)
            )
        # randomly sell something
        if random.choice([True, True, False]):
            sellable_assets = assets[:][assets[AssetProps.FREE] > 0]
            if len(sellable_assets) > 0:
                asset = sellable_assets.sample()
                actions.append(
                    StrategyAction(
                        side="SELL",
                        pair=self._config.TARGET_PAIR,
                        quantity=asset[AssetProps.FREE].values[0]
                    )
                )
        return actions
