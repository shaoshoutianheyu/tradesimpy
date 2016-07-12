from tests_import import *
import unittest
import pandas as pd
import market_data
from TradingAlgorithm import TradingAlgorithm
from Backtester import Backtester
from pprint import pprint


class BacktesterTests(unittest.TestCase):
	def test_backtester_with_one_ticker(self):
		# Initialize market data loading values
		tickers = ['SPY']
		ticker_types = ['']
		data_sources = ['CSV']
		start_date = pd.to_datetime('2016-01-01')
		end_date = pd.to_datetime('2016-5-31')
		history_window = 20
		csv_data_uri = "support_files"

		# Load market data
		data = market_data.load_market_data(tickers, ticker_types, data_sources, start_date, end_date,
			history_window, csv_data_uri)

		# Initialize algorithm values
		algorithm_uri = "support_files/MovingAverageDivergenceAlgorithm.py"
		algorithm_parameters = {
			"ma_long_window"    : 20,
			"ma_short_window"   : 5,
			"open_long"         : -0.25,
			"close_long"        : 0.4,
			"open_short"        : 0.5,
			"close_short"       : -0.15
		}

		# Create trading algorithm
		trading_algorithm = TradingAlgorithm.create_trading_algorithm(algorithm_uri, tickers,
			history_window, algorithm_parameters)

		# Initialize backtester values
		cash = 10000
		commission = 0.0
		ticker_spreads = [0.0001]

		# Setup and run the backtester
		backtester = Backtester(0, trading_algorithm, cash, commission, ticker_spreads)
		results = backtester.run(data, start_date, end_date)
		
		# Check results
		self.assertNotEqual(0, len(results.cash))
		self.assertTrue(len(results.cash) == len(results.invested) == len(results.fees) == len(results.transactions))

	def test_backtester_with_negative_cash(self):
		# Initialize market data loading values
		tickers = ['SPY']
		ticker_types = ['']
		data_sources = ['CSV']
		start_date = pd.to_datetime('2016-01-01')
		end_date = pd.to_datetime('2016-5-31')
		history_window = 20
		csv_data_uri = "support_files"

		# Load market data
		data = market_data.load_market_data(tickers, ticker_types, data_sources, start_date, end_date,
			history_window, csv_data_uri)

		# Initialize algorithm values
		algorithm_uri = "support_files/MovingAverageDivergenceAlgorithm.py"
		algorithm_parameters = {
			"ma_long_window"    : 20,
			"ma_short_window"   : 5,
			"open_long"         : -0.25,
			"close_long"        : 0.4,
			"open_short"        : 0.5,
			"close_short"       : -0.15
		}

		# Create trading algorithm
		trading_algorithm = TradingAlgorithm.create_trading_algorithm(algorithm_uri, tickers,
			history_window, algorithm_parameters)

		# Initialize backtester values
		cash = -10000
		commission = 0.0
		ticker_spreads = [0.0001]

		# Setup and run the backtester
		with self.assertRaises(ValueError):
			backtester = Backtester(0, trading_algorithm, cash, commission, ticker_spreads)
			backtester.run(data, start_date, end_date)

	def test_backtester_with_multiple_ticker(self):
		# Initialize market data loading values
		tickers = ['SPY', 'BND']
		ticker_types = ['', '']
		data_sources = ['CSV', 'CSV']
		start_date = pd.to_datetime('2016-01-01')
		end_date = pd.to_datetime('2016-5-31')
		history_window = 20
		csv_data_uri = "support_files"

		# Load market data
		data = market_data.load_market_data(tickers, ticker_types, data_sources, start_date, end_date,
			history_window, csv_data_uri)

		# Initialize algorithm values
		algorithm_uri = "support_files/MovingAverageDivergenceAlgorithm.py"
		algorithm_parameters = {
			"ma_long_window"    : 20,
			"ma_short_window"   : 5,
			"open_long"         : -0.25,
			"close_long"        : 0.4,
			"open_short"        : 0.5,
			"close_short"       : -0.15
		}

		# Create trading algorithm
		trading_algorithm = TradingAlgorithm.create_trading_algorithm(algorithm_uri, tickers,
			history_window, algorithm_parameters)

		# Initialize backtester values
		cash = 10000
		commission = 0.0
		ticker_spreads = [0.0001]

		# Setup and run the backtester
		backtester = Backtester(0, trading_algorithm, cash, commission, ticker_spreads)
		results = backtester.run(data, start_date, end_date)
		
		# Check results
		self.assertNotEqual(0, len(results.cash))
		self.assertTrue(len(results.cash) == len(results.invested) == len(results.fees) == len(results.transactions))

if __name__ == '__main__':
    unittest.main()
