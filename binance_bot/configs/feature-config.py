import configparser


class FeatureConfig:
    def __init__(self):
        self._configparser = configparser.ConfigParser()
        self._configparser.read(r'configs/feature-config.ini')

        # trend indicators
        # exponential smoothing
        self.EXP_SMOOTHING_ENABLED = self._configparser.get('trend', 'exp_smoothing_enabled') == 'True'
        self.EXP_SMOOTHING_ALPHA = float(self._configparser.get('trend', 'exp_smoothing_alpha'))

        # bollinger bands
        self.BBANDS_PERIOD = int(self._configparser.get('trend', 'bbands_period'))
        self.BBANDS_UPPER = int(self._configparser.get('trend', 'bbands_upper'))
        self.BBANDS_LOWER = int(self._configparser.get('trend', 'bbands_lower'))
        self.BBANDS_MATYPE = int(self._configparser.get('trend', 'bbands_matype'))
        self.BBANDS_REF = self._configparser.get('trend', 'bbands_ref')

        # ema
        self.EMA_PERIOD_SHORT = int(self._configparser.get('trend', 'ema_period_short'))
        self.EMA_PERIOD_MID = int(self._configparser.get('trend', 'ema_period_mid'))
        self.EMA_PERIOD_LONG = int(self._configparser.get('trend', 'ema_period_long'))

        # sma
        self.SMA_PERIOD_SHORT = int(self._configparser.get('trend', 'sma_period_short'))
        self.SMA_PERIOD_MID = int(self._configparser.get('trend', 'sma_period_mid'))
        self.SMA_PERIOD_LONG = int(self._configparser.get('trend', 'sma_period_long'))

        # momentum indicators
        # adx, cci, rsi, roc
        self.ADX_PERIOD = int(self._configparser.get('momentum', 'adx_period'))
        self.CCI_PERIOD = int(self._configparser.get('momentum', 'cci_period'))
        self.RSI_PERIOD = int(self._configparser.get('momentum', 'rsi_period'))
        self.ROC_PERIOD = int(self._configparser.get('momentum', 'roc_period'))

        # stochastic rsi
        self.STOCH_RSI_PERIOD = int(self._configparser.get('momentum', 'stoch_rsi_period'))
        self.FASTK_PERIOD = int(self._configparser.get('momentum', 'fastk_period'))
        self.FASTD_PERIOD = int(self._configparser.get('momentum', 'fastd_period'))
        self.FASTD_MATYPE = int(self._configparser.get('momentum', 'fastd_matype'))

        # williams %r
        self.WILL_R_PERIOD = int(self._configparser.get('momentum', 'will_r_period'))

        # macd
        self.MACD_FASTPERIOD = int(self._configparser.get('momentum', 'macd_fastperiod'))
        self.MACD_SLOWPERIOD = int(self._configparser.get('momentum', 'macd_slowperiod'))
        self.MACD_SIGNALPERIOD = int(self._configparser.get('momentum', 'macd_signalperiod'))
