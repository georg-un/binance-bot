import configparser

from binance_bot.configs.config_utils import getlist


class ClientConfig:
    def __init__(self):
        self._configParser = configparser.ConfigParser()
        self._configParser.read(r'config/client-config.ini')
        self.TARGET_SYMBOL = self._configParser.get('symbols', 'target_symbol')
        self.BASE_SYMBOL = self._configParser.get('symbols', 'base_symbol')
        self.FEATURE_PAIRS = getlist(self._configParser.get('symbols', 'feature_pairs'))
        self.INTERVALS = getlist(self._configParser.get('intervals', 'interval_list'))
        self.TIME_START = getlist(self._configParser.get('time', 'time_start'))
        self.TIME_END = getlist(self._configParser.get('time', 'time_end'))
        self.TARGET_PAIR = self.TARGET_SYMBOL + self.BASE_SYMBOL
