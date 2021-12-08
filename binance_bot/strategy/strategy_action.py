from typing import Literal


class StrategyAction:

    def __init__(self, side: Literal["SELL", "BUY"], pair: str, quantity: float):
        self.side = side
        self.pair = pair
        self.quantity = quantity
