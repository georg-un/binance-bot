from abc import ABC, abstractmethod

import pandas as pd


class AbstractState(ABC):

    klines: pd.DataFrame = None
    features: pd.DataFrame = None
    assets: pd.DataFrame = None

    @abstractmethod
    def next_step(self):
        pass
