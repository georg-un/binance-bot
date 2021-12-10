from binance_bot.client.binance_client import BinanceClient
from binance_bot.configs.main_config import MainConfig
from binance_bot.configs.credentials import Credentials
from binance_bot.configs.feature_config import FeatureConfig
from binance_bot.executor.strategy_executor import StrategyExecutor
from binance_bot.processing.feature_calculator import FeatureCalculator
from binance_bot.state.single_asset_state import SingleAssetState
from binance_bot.strategy.random_strategy import RandomStrategy

main_config = MainConfig()

client = BinanceClient(Credentials())
feature_calc = FeatureCalculator(FeatureConfig())
state = SingleAssetState(client, main_config, feature_calc)
strategy = RandomStrategy(main_config)
executor = StrategyExecutor(client)

state.next_step()
actions = strategy.apply(klines=state.klines, features=state.features, assets=state.assets)
executor.execute(actions)
