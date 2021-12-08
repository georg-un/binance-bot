from binance_bot.client.binance_client import BinanceClient
from binance_bot.configs.client_config import ClientConfig
from binance_bot.configs.credentials import Credentials
from binance_bot.configs.feature_config import FeatureConfig
from binance_bot.executor.strategy_executor import StrategyExecutor
from binance_bot.processing.feature_calculator import FeatureCalculator
from binance_bot.state.default_state import DefaultState
from binance_bot.strategy.random_strategy import RandomStrategy

global_config = ClientConfig()

client = BinanceClient(Credentials())
feature_calc = FeatureCalculator(FeatureConfig())
state = DefaultState(client, global_config, feature_calc)
strategy = RandomStrategy(global_config)
executor = StrategyExecutor(client)

state.next_step()
actions = strategy.apply(klines=state.klines, features=state.features, assets=state.assets)
executor.execute(actions)
