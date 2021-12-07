from abc import ABC, abstractmethod

import numpy as np


class AbstractExecutor(ABC):

    @abstractmethod
    def place_order_buy_market(self, pair: str, quantity: np.double) -> None:
        pass

    @abstractmethod
    def place_order_sell_market(self, pair: str, quantity: np.double) -> None:
        pass
