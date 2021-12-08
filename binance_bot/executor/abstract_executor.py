from abc import ABC, abstractmethod
from typing import List

from binance_bot.strategy.strategy_action import StrategyAction


class AbstractExecutor(ABC):

    @abstractmethod
    def execute(self, actions: List[StrategyAction]) -> None:
        pass
