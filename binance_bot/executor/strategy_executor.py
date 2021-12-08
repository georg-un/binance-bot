from typing import List

from binance_bot.client.binance_client import BinanceClient
from binance_bot.executor.abstract_executor import AbstractExecutor
from binance_bot.strategy.strategy_action import StrategyAction


class StrategyExecutor(AbstractExecutor):

    def __init__(self, client: BinanceClient):
        self._client = client

    def execute(self, actions: List[StrategyAction]) -> None:
        sell_orders = [action for action in actions if action.side == "SELL"]
        buy_orders = [action for action in actions if action.side == "BUY"]
        for order in sell_orders:
            self._client.place_order_sell_market(pair=order.pair, quantity=order.quantity)
        for order in buy_orders:
            self._client.place_order_buy_market(pair=order.pair, quantity=order.quantity)
