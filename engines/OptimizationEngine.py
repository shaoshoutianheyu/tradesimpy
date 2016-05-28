from optimization_engine_import import *
from OptimizationConfiguration import OptimizationConfiguration
from Optimizer import Optimizer
import trading_algorithm_factory as taf
import optimizer_factory as of
import market_data as market_data
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
        optimizer = of.create_optimizer(config.num_processors, config.optimizer_name, trading_algorithm, config.commission,
            config.ticker_spreads, config.optimization_metric, config.optimization_metric_ascending,
            config.optimization_parameters)
        print('Running the optimizer...')
        optimizer.run(data)
        print('Ran optimizer!')
        print

        return optimizer.results
