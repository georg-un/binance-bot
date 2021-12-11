from abc import ABC, abstractmethod

from binance_bot.strategy.strategy_action import StrategyAction


class AbstractExecutor(ABC):

    @abstractmethod
    def execute(self, action: StrategyAction) -> None:
        pass
