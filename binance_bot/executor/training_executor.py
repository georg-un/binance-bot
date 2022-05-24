from typing import List

from binance.exceptions import BinanceAPIException

from binance_bot.client.binance_client import BinanceClient
from binance_bot.configs.main_config import MainConfig
from binance_bot.constants import AssetProps, KlineProps
from binance_bot.executor.abstract_executor import AbstractExecutor
from binance_bot.state.abstract_state import AbstractState
from binance_bot.strategy.strategy_action import StrategyAction


class TrainingExecutor(AbstractExecutor):

    def __init__(self, state: AbstractState, main_config: MainConfig):
        self._state = state
        self._main_config = main_config

    def execute(self, action: StrategyAction) -> None:
        if action is None:
            return
        if action.side == "SELL":
            self._place_sell_order(quantity=action.quantity)
        else:
            self._place_buy_order(quantity=action.quantity)

    def _place_sell_order(self, quantity: float) -> None:
        base_symbol_qty = quantity / self._state.klines[KlineProps.CLOSE].iloc[-1]
        self._state.assets.loc[self._state.assets[AssetProps.ASSET] == self._main_config.TARGET_SYMBOL, AssetProps.FREE] -= quantity
        self._state.assets.loc[self._state.assets[AssetProps.ASSET] == self._main_config.BASE_SYMBOL, AssetProps.FREE] += base_symbol_qty

    def _place_buy_order(self, quantity: float) -> None:
        base_symbol_qty = quantity / self._state.klines[KlineProps.CLOSE].iloc[-1]
        self._state.assets.loc[self._state.assets[AssetProps.ASSET] == self._main_config.TARGET_SYMBOL, AssetProps.FREE] += quantity
        self._state.assets.loc[self._state.assets[AssetProps.ASSET] == self._main_config.BASE_SYMBOL, AssetProps.FREE] -= base_symbol_qty

    # TODO fail if an asset becomes negative
