import configparser


class Credentials:

    def __init__(self):
        self._configParser = configparser.ConfigParser()
        self._configParser.read(r'credentials/binance-api')
        self.API_KEY = self._configParser.get('credentials', 'api_key')
        self.API_SECRET = self._configParser.get('credentials', 'api_secret')
