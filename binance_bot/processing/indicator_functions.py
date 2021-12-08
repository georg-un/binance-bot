import numpy as np
import pandas as pd
import talib

"""
Note: price values have to be multiplied before calculations and divided afterwards due to a bug in talib occuring
with small values (https://github.com/mrjbq7/ta-lib/issues/151)
"""


# INDICATOR FUNCTIONS

def calc_exponential_smoothing(prices: np.ndarray, exp_smoothing_alpha: str) -> np.ndarray:
    smooth_list = pd.DataFrame(prices)
    smooth_list = pd.ewma(smooth_list, alpha=exp_smoothing_alpha)
    return np.array(smooth_list)


# TREND INDICATORS

def calc_bollinger_bands(
        prices: np.ndarray,
        bbands_period: int,
        bbands_lower: int,
        bbands_upper: int,
        bbands_matype: str
) -> np.ndarray:
    """Calculate Bollinger Bands. Return a 2d numpy array containing the three Bollinger Bands."""
    bbands = talib.BBANDS(prices * 10000,
                          timeperiod=bbands_period,
                          nbdevup=bbands_upper,
                          nbdevdn=bbands_lower,
                          matype=bbands_matype)
    # divide results by 10000
    bband_up = bbands[0] / 10000
    bband_mid = bbands[1] / 10000
    bband_low = bbands[2] / 10000
    return np.column_stack((bband_up, bband_mid, bband_low))


def calc_ema(prices: np.ndarray, ema_period_short: int, ema_period_mid: int, ema_period_long: int) -> np.ndarray:
    """Calculate the exponential moving average. Return a 2d numpy array containing the short, mid, and long EMA."""
    ema_short = talib.EMA(prices, timeperiod=ema_period_short)
    ema_mid = talib.EMA(prices, timeperiod=ema_period_mid)
    ema_long = talib.EMA(prices, timeperiod=ema_period_long)
    return np.column_stack((ema_short, ema_mid, ema_long))


def calc_sma(prices: np.ndarray, sma_period_short: int, sma_period_mid: int, sma_period_long: int) -> np.ndarray:
    """Calculate the simple moving average. Return a 2d numpy array containing the short, mid, and long SMA."""
    sma_short = talib.SMA(prices, timeperiod=sma_period_short)
    sma_mid = talib.SMA(prices, timeperiod=sma_period_mid)
    sma_long = talib.SMA(prices, timeperiod=sma_period_long)
    return np.column_stack((sma_short, sma_mid, sma_long))


def calc_typical_price(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
    """Calculate (high + low + close) / 3 to get the typical price of each period.
    Return a 1d numpy array containing the typical price values."""
    return (highs + lows + closes) / 3


# MOMENTUM INDICATORS

def calc_adx(hights: np.ndarray, lows: np.ndarray, closes: np.ndarray, adx_period: int) -> np.ndarray:
    """Calculate the ADX. Return a 1d numpy array containing the ADX-values."""
    return talib.ADX(high=hights, low=lows, close=closes, timeperiod=adx_period)


def calc_cci(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, cci_period: int) -> np.ndarray:
    """Calculate the CCI. Return a 1d numpy array containing the CCI-values."""
    return talib.CCI(high=highs, low=lows, close=closes, timeperiod=cci_period)


def calc_macd(prices: np.ndarray, macd_fastperiod: int, macd_slowperiod: int, macd_signalperiod: int) -> np.ndarray:
    """Calculate the MACD. Return a 2d numpy array containing the MACD, the Signal, and the histogram."""
    macd = talib.MACD(prices * 10000,
                      fastperiod=macd_fastperiod,
                      slowperiod=macd_slowperiod,
                      signalperiod=macd_signalperiod)

    return np.column_stack((macd[0], macd[1], macd[2]))


def calc_rsi(closes: np.ndarray, rsi_period: int) -> np.ndarray:
    """Calculate the RSI. Return a 1d numpy array containing the RSI-values."""
    return talib.RSI(closes * 10000, timeperiod=rsi_period)


def calc_roc(closes: np.ndarray, roc_period: int) -> np.ndarray:
    """Calculate the ROC. Return a 1d numpy array containing the ROC-values."""
    return talib.ROC(closes * 10000, timeperiod=roc_period)


def calc_stoch_rsi(
        closes: np.ndarray,
        stoch_rsi_period: int,
        fastk_period: int,
        fastd_period: int,
        fastd_matype: str
) -> np.ndarray:
    """Calculate the Stochastic RSI. Return a 1d numpy array containing the Stochastic RSI-values."""
    stoch_rsi = talib.STOCHRSI(closes * 10000,
                               timeperiod=stoch_rsi_period,
                               fastk_period=fastk_period,
                               fastd_period=fastd_period,
                               fastd_matype=fastd_matype)
    return np.column_stack((stoch_rsi[0], stoch_rsi[1]))


def calc_will_r(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, will_r_period: int) -> np.ndarray:
    """Calculate the Williams %R. Return a 1d numpy array containing the Williams %R-values."""
    return talib.WILLR(high=highs, low=lows, close=closes, timeperiod=will_r_period)


# VOLUME INDICATORS

def calc_obv(prices: np.ndarray, volumes: np.ndarray) -> np.ndarray:
    """Calculate the On Balance Volume. Return a 1d numpy array containing the OBV-values."""
    return talib.OBV(prices, volumes)


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
