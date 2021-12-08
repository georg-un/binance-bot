import configparser

from binance_bot.configs.config_utils import getlist


class ClientConfig:
    def __init__(self):
        self._configParser = configparser.ConfigParser()
        self._configParser.read(r'config/client-config.ini')
        self.PAIRS = getlist(self._configParser.get('pairs', 'pair_list'))
        self.SYMBOLS = getlist(self._configParser.get('symbols', 'symbols'))
        self.INTERVALS = getlist(self._configParser.get('intervals', 'interval_list'))
        self.TIME_START = getlist(self._configParser.get('time', 'time_start'))
        self.TIME_END = getlist(self._configParser.get('time', 'time_end'))
