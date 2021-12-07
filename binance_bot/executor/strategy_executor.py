import numpy as np

from binance_bot.binance.binance_client import BinanceClient
from binance_bot.executor.abstract_executor import AbstractExecutor


class StrategyExecutor(AbstractExecutor):

    def __init__(self, binance_client: BinanceClient):
        self.binance_client = binance_client

    def place_order_sell_market(self, pair: str, quantity: np.double) -> None:
        self.binance_client.place_order_sell_market(pair=pair, quantity=quantity)

    def place_order_buy_market(self, pair: str, quantity: np.double) -> None:
        self.binance_client.place_order_buy_market(pair=pair, quantity=quantity)
