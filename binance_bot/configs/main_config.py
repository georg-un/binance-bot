import configparser

from binance_bot.configs.config_utils import getlist


class MainConfig:
    def __init__(self):
        self._configParser = configparser.ConfigParser()
        self._configParser.read(r'config/main-config.ini')
        self.TARGET_SYMBOL = self._configParser.get('symbols', 'target_symbol')
        self.BASE_SYMBOL = self._configParser.get('symbols', 'base_symbol')
        self.FEATURE_PAIRS = getlist(self._configParser.get('symbols', 'feature_pairs'))
        self.INTERVALS = getlist(self._configParser.get('intervals', 'interval_list'))
        self.TARGET_PAIR = self.TARGET_SYMBOL + self.BASE_SYMBOL
        self.DATABASE_CONFIG = DatabaseConfig(
            host=self._configParser.get('database', 'host'),
            port=int(self._configParser.get('database', 'port')),
            dbname=self._configParser.get('database', 'dbname'),
            user=self._configParser.get('database', 'user'),
            password=self._configParser.get('database', 'password')
        )


class DatabaseConfig:
    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
