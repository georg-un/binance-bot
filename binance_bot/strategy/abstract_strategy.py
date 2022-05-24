from abc import abstractmethod, ABC
from typing import List

import pandas as pd

from binance_bot.strategy.strategy_action import StrategyAction


class AbstractStrategy(ABC):

    @abstractmethod
    def apply(
            self,
            klines: pd.DataFrame,
            features: pd.DataFrame,
            assets: pd.DataFrame
    ) -> List[StrategyAction]:
        pass
