from typing import Literal

import numpy as np


class StrategyAction:

    def __init__(self, side: Literal["SELL", "BUY"], pair: str, quantity: np.double):
        self.side = side
        self.pair = pair
        self.quantity = quantity
