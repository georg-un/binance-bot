import datetime as dt

import numpy as np
import pandas as pd
from binance.client import Client

from binance_bot.configs.credentials import Credentials
from binance_bot.constants import KlineProps, OrderProps


class BinanceClient:

    def __init__(self, credentials: Credentials):
        self._client = Client(api_key=credentials.API_KEY, api_secret=credentials.API_SECRET)

    def place_order_sell_market(self, pair: str, quantity: np.double) -> None:
        self._client.create_test_order(
            symbol=pair,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity
        )

    def place_order_buy_market(self, pair: str, quantity) -> None:
        self._client.create_test_order(
            symbol=pair,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity
        )

    def get_historical_data(self, pair: str, interval: str, time_start: str, time_end: str) -> pd.DataFrame:
        response = self._client.get_historical_klines(
            symbol=pair,
            interval=interval,
            start_str=time_start,
            end_str=time_end
        )
        return self._klines_to_dataframe(np.array(response))

    def get_klines(self, pair: str, interval: str) -> pd.DataFrame:
        response = self._client.get_klines(symbol=pair, interval=interval)
        return self._klines_to_dataframe(np.array(response))

    def get_open_orders(self) -> pd.DataFrame:
        return pd.DataFrame(self._client.get_open_orders())

    def get_assets(self, symbols: str) -> pd.DataFrame:
        return pd.DataFrame([self._client.get_asset_balance(asset=asset) for asset in symbols])

    @staticmethod
    def api_time_format(ms: int):
        """Convert a unix timestamp in milliseconds to the date-format required by binance.client."""
        timestamp = dt.datetime.fromtimestamp(ms / 1000)
        time_str = dt.date.strftime(timestamp, '%B %d, %Y %H:%M:%S')
        return time_str

    @staticmethod
    def _klines_to_dataframe(klines: np.ndarray) -> pd.DataFrame:
        """
        Convert the response from the klines-API to a dataframe.
        https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data
        """
        return pd.DataFrame({
            KlineProps.TIME_OPEN: klines[:, 0],
            KlineProps.OPEN: klines[:, 1],
            KlineProps.HIGH: klines[:, 2],
            KlineProps.LOW: klines[:, 3],
            KlineProps.CLOSE: klines[:, 4],
            KlineProps.VOLUME: klines[:, 5]
        }).astype(float)
