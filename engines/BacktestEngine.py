from backtest_engine_import import *
from BacktestConfiguration import BacktestConfiguration
from Backtester import Backtester
import trading_algorithms.TradingAlgorithmFactory as taf
import data.market_data as market_data


class BacktestEngine(object):

    def __init__(self):
        pass

    def run(self, config):
        # Load market data
        data = market_data.load_market_data(config.tickers, config.ticker_types, config.data_sources, \
            config.start_date, config.end_date, config.history_window)

        # Create the trading algorithm
        trading_algo = taf.create_trading_algorithm(config.algorithm_name, config.tickers, config.history_window, \
            config.algorithm_parameters)

        # Setup and run the backtester
        backtester = Backtester(0, config.cash, config.commission, config.ticker_spreads)
        print('Running the backtester...')
        backtester.run(trading_algo, data)
        print('Ran backtester!')
        print

        return backtester.results
