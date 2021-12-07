from typing import Dict

from binance_bot.configs.feature_config import FeatureConfig
from binance_bot.processing.indicator_functions import *


class FeatureCalculator:

    def __init__(self, feature_config: FeatureConfig):
        self._config = feature_config

    def calculate_features(
            self,
            times_open: np.ndarray,
            highs: np.ndarray,
            lows: np.ndarray,
            opens: np.ndarray,
            closes: np.ndarray,
            volumes: np.ndarray
    ) -> Dict[str, np.ndarra]:
        features: Dict[str, np.ndarray] = {}

        if self._config.EXP_SMOOTHING_ENABLED:
            highs = calc_exponential_smoothing(values=highs, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)
            lows = calc_exponential_smoothing(values=lows, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)
            opens = calc_exponential_smoothing(values=opens, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)
            closes = calc_exponential_smoothing(values=closes, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)
            volumes = calc_exponential_smoothing(values=volumes, exp_smoothing_alpha=self._config.EXP_SMOOTHING_ALPHA)

        features["bollinger"] = calc_bollinger_bands(
            prices=closes,
            timestamps=times_open,
            bbands_period=self._config.BBANDS_PERIOD,
            bbands_lower=self._config.BBANDS_LOWER,
            bbands_upper=self._config.BBANDS_UPPER,
            bbands_matype=self._config.BBANDS_MATYPE
        )

        features["ema"] = calc_ema(
            prices=closes,
            timestamps=times_open,
            ema_period_short=self._config.EMA_PERIOD_SHORT,
            ema_period_mid=self._config.EMA_PERIOD_MID,
            ema_period_long=self._config.EMA_PERIOD_LONG
        )

        features["macd"] = calc_macd(
            prices=closes,
            timestamps=times_open,
            macd_fastperiod=self._config.MACD_FASTPERIOD,
            macd_slowperiod=self._config.MACD_SLOWPERIOD,
            macd_signalperiod=self._config.MACD_SIGNALPERIOD
        )

        features["obv"] = calc_obv(
            prices=closes,
            volumes=volumes,
            timestamps=times_open
        )

        return features