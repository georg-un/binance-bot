import numpy as np
import pandas as pd
import talib

from binance_bot.constants import Indicators

"""
Note: price values have to be multiplied before calculations and divided afterwards due to a bug in talib occuring
with small values (https://github.com/mrjbq7/ta-lib/issues/151)
"""


# INDICATOR FUNCTIONS

def calc_exponential_smoothing(prices: pd.Series, exp_smoothing_alpha: float) -> pd.Series:
    return prices.ewm(alpha=exp_smoothing_alpha).mean()


# TREND INDICATORS

def calc_bollinger_bands(
        prices: np.ndarray,
        bbands_period: int,
        bbands_lower: int,
        bbands_upper: int,
        bbands_matype: str
) -> pd.DataFrame:
    """Calculate Bollinger Bands. Return a pandas dataframe containing the three Bollinger Bands."""
    bbands = talib.BBANDS(prices * 10000,
                          timeperiod=bbands_period,
                          nbdevup=bbands_upper,
                          nbdevdn=bbands_lower,
                          matype=bbands_matype)
    return pd.DataFrame({
        Indicators.BOLL_UP: bbands[0] / 10000,
        Indicators.BOLL_MID: bbands[1] / 10000,
        Indicators.BOLL_LOW: bbands[2] / 10000
    })


def calc_ema(prices: np.ndarray, ema_period_short: int, ema_period_mid: int, ema_period_long: int) -> pd.DataFrame:
    """Calculate the exponential moving average. Return a pandas dataframe containing the short, mid, and long EMA."""
    return pd.DataFrame({
        Indicators.EMA_SHORT: talib.EMA(prices, timeperiod=ema_period_short),
        Indicators.EMA_MID: talib.EMA(prices, timeperiod=ema_period_mid),
        Indicators.EMA_LONG: talib.EMA(prices, timeperiod=ema_period_long)
    })


def calc_sma(prices: np.ndarray, sma_period_short: int, sma_period_mid: int, sma_period_long: int) -> pd.DataFrame:
    """Calculate the simple moving average. Return a pandas dataframe containing the short, mid, and long SMA."""
    return pd.DataFrame({
        Indicators.SMA_SHORT: talib.SMA(prices, timeperiod=sma_period_short),
        Indicators.SMA_MID: talib.SMA(prices, timeperiod=sma_period_mid),
        Indicators.SMA_LONG: talib.SMA(prices, timeperiod=sma_period_long)
    })


def calc_typical_price(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> pd.Series:
    """Calculate (high + low + close) / 3 to get the typical price of each period.
    Return a 1d numpy array containing the typical price values."""
    return pd.Series((highs + lows + closes) / 3, name=Indicators.TYPICAL_PRICE)


# MOMENTUM INDICATORS

def calc_adx(hights: np.ndarray, lows: np.ndarray, closes: np.ndarray, adx_period: int) -> pd.Series:
    """Calculate the ADX. Return a 1d numpy array containing the ADX-values."""
    return pd.Series(talib.ADX(high=hights, low=lows, close=closes, timeperiod=adx_period), name=Indicators.ADX)


def calc_cci(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, cci_period: int) -> pd.Series:
    """Calculate the CCI. Return a 1d numpy array containing the CCI-values."""
    return pd.Series(talib.CCI(high=highs, low=lows, close=closes, timeperiod=cci_period), name=Indicators.CCI)


def calc_macd(prices: np.ndarray, macd_fastperiod: int, macd_slowperiod: int, macd_signalperiod: int) -> pd.DataFrame:
    """Calculate the MACD. Return a 2d numpy array containing the MACD, the Signal, and the histogram."""
    macd = talib.MACD(prices * 10000,
                      fastperiod=macd_fastperiod,
                      slowperiod=macd_slowperiod,
                      signalperiod=macd_signalperiod)
    return pd.DataFrame({
        Indicators.MACD: macd[0],
        Indicators.MACD_SIGNAL: macd[1],
        Indicators.MACD_HIST: macd[2]
    })


def calc_rsi(closes: np.ndarray, rsi_period: int) -> pd.Series:
    """Calculate the RSI. Return a 1d numpy array containing the RSI-values."""
    return pd.Series(talib.RSI(closes * 10000, timeperiod=rsi_period), name=Indicators.RSI)


def calc_roc(closes: np.ndarray, roc_period: int) -> pd.Series:
    """Calculate the ROC. Return a 1d numpy array containing the ROC-values."""
    return pd.Series(talib.ROC(closes * 10000, timeperiod=roc_period), name=Indicators.ROC)


def calc_stoch_rsi(
        closes: np.ndarray,
        stoch_rsi_period: int,
        fastk_period: int,
        fastd_period: int,
        fastd_matype: str
) -> pd.DataFrame:
    """Calculate the Stochastic RSI. Return a 1d numpy array containing the Stochastic RSI-values."""
    stoch_rsi = talib.STOCHRSI(closes * 10000,
                               timeperiod=stoch_rsi_period,
                               fastk_period=fastk_period,
                               fastd_period=fastd_period,
                               fastd_matype=fastd_matype)
    return pd.DataFrame({
        Indicators.STOCH_RSI_FASTK: stoch_rsi[0],
        Indicators.STOCH_RSI_FASTD: stoch_rsi[1]
    })


def calc_will_r(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, will_r_period: int) -> pd.Series:
    """Calculate the Williams %R. Return a 1d numpy array containing the Williams %R-values."""
    return pd.Series(talib.WILLR(high=highs, low=lows, close=closes, timeperiod=will_r_period), name=Indicators.WILL_R)


# VOLUME INDICATORS

def calc_obv(prices: np.ndarray, volumes: np.ndarray) -> pd.Series:
    """Calculate the On Balance Volume. Return a 1d numpy array containing the OBV-values."""
    return pd.Series(talib.OBV(prices, volumes), name=Indicators.OBV)


# TODO check if this function is still needed
def calc_return(data_array, f_horizon):
    """
    Args:
        data_array: A 1-dimensional numpy array containing the closing price of each period

        f_horizon: An integer determining the base-period which shall be used to calculate the return
                   e.g. if f_horizon==4 then the return is calculated as ((price at t4 / price at t0) -1)

    Returns:
        A 1-dimensional numpy array containing the return values for each period (shortened by the number of f_horizon)
    """

    return_array = (
            (data_array[f_horizon:] /
             data_array[:len(data_array) - f_horizon]) - 1
    )

    return return_array
