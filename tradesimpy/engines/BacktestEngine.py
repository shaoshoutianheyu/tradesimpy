from backtest_engine_import import *
from Backtester import Backtester
from TradingAlgorithm import TradingAlgorithm
import market_data as market_data
import logger
import logging as log


class BacktestEngine(object):

    def __init__(self):
        pass

    def run(self, config):
        logger.init_logger(config.log_uri)

        # Load market data
        log.info('Loading data...')
        data = market_data.load_market_data(config.tickers, config.ticker_types, config.data_sources, \
            config.start_date, config.end_date, config.history_window, config.csv_data_uri)
        log.info('Data loaded!')
        print

        # Create the trading algorithm
        trading_algorithm = TradingAlgorithm.create_trading_algorithm(config.algorithm_uri, config.tickers, \
            config.history_window, config.algorithm_parameters)

        # Setup and run the backtester
        backtester = Backtester(0, trading_algorithm, config.cash, config.commission, config.ticker_spreads)
        log.info('Running the backtester...')
        backtester.run(data, config.start_date, config.end_date)
        log.info('Ran backtester!')
        print

        return backtester.results
