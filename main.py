import time

from binance.helpers import interval_to_milliseconds

from binance_bot.client.binance_client import BinanceClient
from binance_bot.configs.credentials import Credentials
from binance_bot.configs.feature_config import FeatureConfig
from binance_bot.configs.main_config import MainConfig
from binance_bot.constants import KlineProps
from binance_bot.executor.strategy_executor import StrategyExecutor
from binance_bot.processing.feature_calculator import FeatureCalculator
from binance_bot.state.single_asset_state import SingleAssetState, DataFrameMissmatchError
from binance_bot.strategy.random_strategy import RandomStrategy

main_config = MainConfig()
INTERVAL_MS = interval_to_milliseconds(main_config.TARGET_INTERVAL)

client = BinanceClient(Credentials())
feature_calc = FeatureCalculator(FeatureConfig())
state = SingleAssetState(client, main_config, feature_calc)
strategy = RandomStrategy(main_config)
executor = StrategyExecutor(client)

last_kline_timestamp = 0
while True:
    if time.time() * 1000 < last_kline_timestamp:
        print("waiting 5s")
        time.sleep(5)
    else:
        try:
            state.next_step()
            action = strategy.apply(klines=state.klines, features=state.features, assets=state.assets)
            executor.execute(action)
            last_kline_timestamp = state.klines[KlineProps.TIME_OPEN].iloc[-1] + INTERVAL_MS
        except DataFrameMissmatchError as e:
            print(str(e), "Retrying...")
            time.sleep(5)
