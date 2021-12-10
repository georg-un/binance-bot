from typing import Dict, List, Union

import pandas as pd

from binance_bot.configs.feature_config import FeatureConfig
from binance_bot.constants import KlineProps
from binance_bot.processing.indicator_functions import *


class FeatureCalculator:

    def __init__(self, feature_config: FeatureConfig):
        self._config = feature_config

    def calculate_features(
            self,
            klines: pd.DataFrame,
            additional_features: pd.DataFrame = None
    ) -> pd.DataFrame:
        opens = klines[KlineProps.OPEN]
        highs = klines[KlineProps.HIGH]
        lows = klines[KlineProps.LOW]
        closes = klines[KlineProps.CLOSE]
        volumes = klines[KlineProps.VOLUME]

        if self._config.EXP_SMOOTHING_ENABLED:
            highs = calc_exponential_smoothing(prices=highs, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)
            lows = calc_exponential_smoothing(prices=lows, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)
            opens = calc_exponential_smoothing(prices=opens, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)
            closes = calc_exponential_smoothing(prices=closes, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)
            volumes = calc_exponential_smoothing(prices=volumes, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)

        features: List[Union[pd.DataFrame, pd.Series]] = [
            calc_bollinger_bands(
                prices=closes,
                bbands_period=self._config.BBANDS_PERIOD,
                bbands_lower=self._config.BBANDS_LOWER,
                bbands_upper=self._config.BBANDS_UPPER,
                bbands_matype=self._config.BBANDS_MATYPE
            ),
            calc_ema(
                prices=closes,
                ema_period_short=self._config.EMA_PERIOD_SHORT,
                ema_period_mid=self._config.EMA_PERIOD_MID,
                ema_period_long=self._config.EMA_PERIOD_LONG
            ),
            calc_macd(
                prices=closes,
                macd_fastperiod=self._config.MACD_FASTPERIOD,
                macd_slowperiod=self._config.MACD_SLOWPERIOD,
                macd_signalperiod=self._config.MACD_SIGNALPERIOD
            ),
            calc_obv(
                prices=closes,
                volumes=volumes
            ),
            additional_features
        ]
        return pd.concat(features, axis=1)
