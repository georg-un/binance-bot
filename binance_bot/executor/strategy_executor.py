from binance.exceptions import BinanceAPIException

from binance_bot.client.binance_client import BinanceClient
from binance_bot.executor.abstract_executor import AbstractExecutor
from binance_bot.strategy.strategy_action import StrategyAction


class StrategyExecutor(AbstractExecutor):

    def __init__(self, client: BinanceClient):
        self._client = client

    def execute(self, action: StrategyAction) -> None:
        try:
            if action.side == "SELL":
                self._client.place_order_sell_market(pair=action.pair, quantity=action.quantity)
            else:
                self._client.place_order_buy_market(pair=action.pair, quantity=action.quantity)
        except BinanceAPIException as e:
            print(e)
