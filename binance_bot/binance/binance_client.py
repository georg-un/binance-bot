import numpy as np
import binance.enums as bi

from binance.client import Client


class BinanceClient:

    def __init__(self, client: Client):
        self.client = client

    def place_order_sell_market(self, pair: str, quantity: np.double) -> None:
        self.client.create_test_order(symbol=pair, side=bi.SIDE_SELL, type=bi.ORDER_TYPE_MARKET, quantity=quantity)

    def place_order_buy_market(self, pair: str, quantity):
        self.client.create_test_order(symbol=pair, side=bi.SIDE_BUY, type=bi.ORDER_TYPE_MARKET, quantity=quantity)
