import random
from typing import List

import pandas as pd

from binance_bot.configs.client_config import ClientConfig
from binance_bot.constants import AssetProps
from binance_bot.strategy.abstract_strategy import AbstractStrategy
from binance_bot.strategy.strategy_action import StrategyAction


class RandomStrategy(AbstractStrategy):

    def __init__(self, global_config: ClientConfig):
        self._config = global_config

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
                StrategyAction(side="BUY", pair=random.choice(self._config.PAIRS), quantity=1.0)
            )
        # randomly sell something
        if random.choice([True, True, False]):
            sellable_assets = assets[:][assets[AssetProps.FREE] > 0]
            if len(sellable_assets) > 0:
                asset = sellable_assets.sample()
                actions.append(
                    StrategyAction(
                        side="SELL",
                        pair=asset[AssetProps.ASSET].values[0] + self._config.BASE_SYMBOL,
                        quantity=asset[AssetProps.FREE].values[0]
                    )
                )
        return actions
