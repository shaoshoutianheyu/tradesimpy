from backtest_engine_import import *
from BacktestConfiguration import BacktestConfiguration
import trading_algorithms.TradingAlgorithmFactory as taf
from Backtester import Backtester
import json
import re
import pandas as pd
from pandas.tseries.offsets import BDay
from pprint import pprint
import Quandl

QUANDL_API_KEY = 'B8h6uA58skuqwcAtL_tf'


class BacktestEngine(object):

    def __init__(self):
        pass

    def run(self, config):
        # TODO: Package this data loading part in some generic data loading class
        # Determine the series data to load from Quandl
        ticker_count = len(config.tickers)
        data_request = [config.ticker_types[i] + "/" + config.tickers[i] for i in range(ticker_count)]

        # TODO: Package this data loading part in some Quandl specific data loading class
        # Pull series data between given date range while accommodating for the history window
        data_start_date = config.start_date - BDay(config.history_window + 5)
        data = Quandl.get(data_request, trim_start=data_start_date, trim_end=config.end_date, authtoken=QUANDL_API_KEY)

        # Prepare data dictionary
        data_dict = {}
        for ticker in config.tickers:
            data_dict[ticker] = {}

        # TODO: Package this data loading part in some generic data loading class
        # Discover data needed for analysis process, especially for history windows
        for column_name, series in data.iteritems():
            start_date = config.start_date

            # Start on valid date
            while start_date not in series.index:
                start_date += BDay(1)

            # Determine pure ticker and series name associated with column series
            series_name = re.sub("^[\s\w.]+-\s+", "", column_name)
            ticker = re.sub("\s-[\s\w]+$", "", column_name)
            ticker = re.sub("^\w+.", "", ticker)

            # Grab only the required data specified by the history window
            start_period = data[column_name][:start_date].sort_index(ascending=False)
            hist_start_date = start_period.index[config.history_window].to_datetime()
            data_dict[ticker][series_name] = data[column_name][hist_start_date:]

        # Save backtest data
        backtest_data = {}
        for ticker in config.tickers:
            backtest_data[ticker] = pd.DataFrame(data_dict[ticker])

        # Create the trading algorithm
        trading_algo = taf.create_trading_algo(config.algorithm_name, config.tickers, config.history_window, config.algorithm_parameters)

        # Setup and run the backtester
        backtester = Backtester(config.cash, config.commission, config.ticker_spreads)
        backtester.run(config.cash, trading_algo, backtest_data)

        # Save results
        self.results = backtester.results
