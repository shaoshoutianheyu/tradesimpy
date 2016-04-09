from backtest_engine_import import *
from BacktestConfiguration import BacktestConfiguration
import trading_algorithms.TradingAlgorithmFactory as taf
import data.MarketData as market_data
from Backtester import Backtester
import json
import re
import pandas as pd
from pandas.tseries.offsets import BDay
from pprint import pprint
import Quandl


class BacktestEngine(object):

    def __init__(self):
        pass

    def run(self, config):
        backtest_data = market_data.load_market_data(config.tickers, config.ticker_types, config.data_sources, \
            config.start_date, config.end_date, config.history_window)

        #pprint(backtest_data)
        #exit(0)

        # Create the trading algorithm
        trading_algo = taf.create_trading_algo(config.algorithm_name, config.tickers, config.history_window, \
            config.algorithm_parameters)

        # Setup and run the backtester
        backtester = Backtester(config.cash, config.commission, config.ticker_spreads)
        backtester.run(config.cash, trading_algo, backtest_data)

        # Save results
        self.results = backtester.results
