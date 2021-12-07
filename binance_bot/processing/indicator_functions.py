import numpy as np
import pandas as pd
import talib


# INDICATOR FUNCTIONS

def calc_exponential_smoothing(values: np.ndarray, exp_smoothing_alpha: str) -> np.ndarray:
    smooth_list = np.array([i[0] for i in values])
    smooth_list = pd.DataFrame(smooth_list)
    smooth_list = pd.ewma(smooth_list, alpha=exp_smoothing_alpha)
    return np.array(smooth_list)


# TREND INDICATORS

def calc_bollinger_bands(
        values: np.ndarray,
        timestamps: np.ndarray,
        bbands_period: int,
        bbands_lower: int,
        bbands_upper: int,
        bbands_matype: str
) -> np.ndarray:
    """Calculate Bollinger Bands given a price list and parameters from config.txt. Return a 4-dimensional numpy array
    containing the three Bollinger Bands as well as date values.
    Note: price values have to be multiplied before calculations and divided afterwards due to a bug in talib occuring
    with small values (https://github.com/mrjbq7/ta-lib/issues/151)"""

    # calculate bollinger bands
    results_list = talib.BBANDS(values * 10000,
                                timeperiod=bbands_period,
                                nbdevup=bbands_upper,
                                nbdevdn=bbands_lower,
                                matype=bbands_matype)

    # divide results by 100000
    bband_up = results_list[0] / 10000
    bband_mid = results_list[1] / 10000
    bband_low = results_list[2] / 10000

    # construct 4d-array and return it
    bollinger_array = np.column_stack((bband_up, bband_mid, bband_low, timestamps))
    return bollinger_array


def calc_ema(
        values: np.ndarray,
        timestamps: np.ndarray,
        ema_period_short: int,
        ema_period_mid: int,
        ema_period_long: int
) -> np.ndarray:
    # calculate an ema for each period
    ema_short = talib.EMA(values,
                          timeperiod=ema_period_short)
    ema_mid = talib.EMA(values,
                        timeperiod=ema_period_mid)
    ema_long = talib.EMA(values,
                         timeperiod=ema_period_long)
    # construct 4d-array and return it
    ema = np.column_stack((ema_short, ema_mid, ema_long,
                           np.array([i[0] for i in timestamps])))
    return ema


def calc_sma(
        values: np.ndarray,
        timestamps: np.ndarray,
        sma_period_short: int,
        sma_period_mid: int,
        sma_period_long: int
) -> np.ndarray:
    # calculate an ema for each period
    sma_short = talib.SMA(values,
                          timeperiod=sma_period_short)
    sma_mid = talib.SMA(values,
                        timeperiod=sma_period_mid)
    sma_long = talib.SMA(values,
                         timeperiod=sma_period_long)

    # construct 4d-array and return it
    sma = np.column_stack((sma_short, sma_mid, sma_long,
                           np.array([i[0] for i in timestamps])))
    return sma


def calc_typical_price(
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        timestamps: np.ndarray
) -> np.ndarray:
    """Take price-lists for high, low and close and calculate (high + low + close) / 3 to get
    the typical price of a period. Return a two dimensional numpy-array containing the typical price values
    as well as date values."""

    # initialize array
    price_array = np.array([], dtype='double')

    # calculate (high + low + close) / 3 for each row
    for element in range(0, len(closes)):
        typical_price = (highs[element][0] +
                         lows[element][0] +
                         closes[element][0]) / 3

        price_array = np.append(price_array, typical_price)

    # get date array
    date_array = np.array([i[0] for i in timestamps])

    # add both arrays to a 2-dimensional array
    typ_price_array = np.column_stack((price_array, date_array))

    return typ_price_array


# MOMENTUM INDICATORS

def calc_adx(
        hights: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        timestamps: np.ndarray,
        adx_period: int
) -> np.ndarray:
    """Calculate ADX given high, low and close values as well as a period-parameter from config.txt. Return a
       2-dimensional numpy array containing the ADX-values and the respective timestamps."""

    # calculate adx
    adx = talib.ADX(high=np.array([i[0] for i in hights]),
                    low=np.array([i[0] for i in lows]),
                    close=np.array([i[0] for i in closes]),
                    timeperiod=adx_period)

    # combine adx-array with timestamps and return it
    adx = np.column_stack((adx, np.array([i[0] for i in timestamps])))
    return adx


def calc_cci(
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        timestamps: np.ndarray,
        cci_period: int
) -> np.ndarray:
    """Calculate CCI given high, low and close values as well as a period-parameter from config.txt. Return a
       2-dimensional numpy array containing the CCI-values and the respective timestamps."""

    # calculate cci
    cci = talib.CCI(high=np.array([i[0] for i in highs]),
                    low=np.array([i[0] for i in lows]),
                    close=np.array([i[0] for i in closes]),
                    timeperiod=cci_period)

    # combine cci-array with timestamps and return it
    cci = np.column_stack((cci, np.array([i[0] for i in timestamps])))
    return cci


def calc_macd(
        prices: np.ndarray,
        timestamps: np.ndarray,
        macd_fastperiod: int,
        macd_slowperiod: int,
        macd_signalperiod: int
) -> np.ndarray:
    """Calculate MACD given price values as well as period-parameters from config.txt. Return a
           4-dimensional numpy array containing the MACD, the Signal, the histogram and the respective timestamps."""
    macd = talib.MACD(np.array([i[0] * 10000 for i in prices]),
                      fastperiod=macd_fastperiod,
                      slowperiod=macd_slowperiod,
                      signalperiod=macd_signalperiod)

    macd = np.column_stack((macd[0],
                            macd[1],
                            macd[2],
                            np.array([i[0] for i in timestamps])))

    return macd


def calc_rsi(closes: np.ndarray, timestamps: np.ndarray, rsi_period: int) -> np.ndarray:
    """Calculate RSI given only close values as well as a period-parameter from config.txt. Return a
       2-dimensional numpy array containing the RSI-values and the respective timestamps."""

    # calculate rsi
    rsi = talib.RSI(np.array([i[0] * 10000 for i in closes]),
                    timeperiod=rsi_period)

    # combine rsi-array with timestamps and return it
    rsi = np.column_stack((rsi, np.array([i[0] for i in timestamps])))
    return rsi


def calc_roc(closes: np.ndarray, timestamps: np.ndarray, roc_period: int) -> np.ndarray:
    """Calculate ROC given only close values as well as a period-parameter from config.txt. Return a
           2-dimensional numpy array containing the ROC-values and the respective timestamps."""

    # calculate roc
    roc = talib.ROC(np.array([i[0] * 10000 for i in closes]),
                    timeperiod=roc_period)

    # combine roc-array with timestamps and return it
    roc = np.column_stack((roc, np.array([i[0] for i in timestamps])))
    return roc


def calc_stoch_rsi(
        closes: np.ndarray,
        timestamps: np.ndarray,
        stoch_rsi_period: int,
        fastk_period: int,
        fastd_period: int,
        fastd_matype: str
) -> np.ndarray:
    """Calculate Stochastic RSI given only close values as well as parameters from config.txt. Return a
       2-dimensional numpy array containing the Stochastic RSI-values and the respective timestamps."""

    # calculate stochastic rsi
    stoch_rsi = talib.STOCHRSI(np.array([i[0] * 10000 for i in closes]),
                               timeperiod=stoch_rsi_period,
                               fastk_period=fastk_period,
                               fastd_period=fastd_period,
                               fastd_matype=fastd_matype)

    # construct 4-dimensional array and return it
    stoch_rsi = np.column_stack((stoch_rsi[0], stoch_rsi[1], np.array([i[0] for i in timestamps])))
    return stoch_rsi


def calc_will_r(
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        timestamps: np.ndarray,
        will_r_period: int
) -> np.ndarray:
    """Calculate Williams %R given high, low & close values as well as a period-parameter from config.txt. Return a
       2-dimensional numpy array containing the Williams %R-values and the respective timestamps."""

    # calculate williams %r
    will_r = talib.WILLR(high=np.array([i[0] for i in highs]),
                         low=np.array([i[0] for i in lows]),
                         close=np.array([i[0] for i in closes]),
                         timeperiod=will_r_period)

    # add timestamps and return array
    will_r = np.column_stack((will_r, np.array([i[0] for i in timestamps])))
    return will_r


# VOLUME INDICATORS

def calc_obv(prices: np.ndarray, volumes: np.ndarray, timestamps: np.ndarray) -> np.ndarray:
    """Calculate On Balance Volume given price and volume values. Return a 2-dimensional numpy array
       containing the OBV-values and the respective timestamps."""

    # calculate obv
    obv = talib.OBV(np.array([i[0] for i in prices]),
                    np.array([i[0] for i in volumes]))

    # add timestamps and return array
    obv = np.column_stack((obv, np.array([i[0] for i in timestamps])))
    return obv


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
         data_array[:len(data_array)-f_horizon]) - 1
    )

    return return_array
