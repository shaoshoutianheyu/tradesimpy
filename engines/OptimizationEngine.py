from optimization_engine_import import *
from OptimizationConfiguration import OptimizationConfiguration
from Optimizer import Optimizer
import trading_algorithms.TradingAlgorithmFactory as taf
import optimizers.OptimizerFactory as of
import data.MarketData as market_data
from pprint import pprint


class OptimizationEngine(object):

    def __init__(self):
        pass

    def run(self, config):
        # Load market data
        data = market_data.load_market_data(config.tickers, config.ticker_types, config.data_sources, \
            config.start_date, config.end_date, config.history_window)

        # Create the trading algorithm w/o parameters
        trading_algorithm = taf.create_trading_algorithm(config.algorithm_name, config.tickers, config.history_window)

        # Setup and run the optimizer
        optimizer = of.create_optimizer(config.optimizer_name, trading_algorithm, config.commission,
            config.ticker_spreads, config.optimization_metric, config.optimization_metric_ascending,
            config.optimization_parameters)
        optimizer.run(data)
        
        # Save results
        #self.results = backtester.results
