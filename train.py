import time

from binance.helpers import interval_to_milliseconds

from binance_bot.client.binance_client import BinanceClient
from binance_bot.configs.credentials import Credentials
from binance_bot.configs.feature_config import FeatureConfig
from binance_bot.configs.main_config import MainConfig
from binance_bot.constants import KlineProps
from binance_bot.executor.strategy_executor import StrategyExecutor
from binance_bot.executor.training_executor import TrainingExecutor
from binance_bot.processing.feature_calculator import FeatureCalculator
from binance_bot.state.single_asset_state import SingleAssetState, DataFrameMissmatchError
from binance_bot.state.training_state import TrainingState
from binance_bot.strategy.random_strategy import RandomStrategy

main_config = MainConfig()

feature_calc = FeatureCalculator(FeatureConfig())
state = TrainingState(main_config=main_config, feature_calculator=feature_calc)
strategy = RandomStrategy(main_config)
executor = TrainingExecutor(state=state, main_config=main_config)


EPOCHS = 100

for epoch in range(0, EPOCHS):
    state.next_batch()
    for _ in range(0, state.BATCH_SIZE):
        state.next_step()
        print("Current asset value:", str(state.get_total_asset_value()))
        action = strategy.apply(klines=state.klines, features=state.features, assets=state.assets)
        executor.execute(action)
    print("################ Asset value at end of epoch:", str(state.get_total_asset_value()))
