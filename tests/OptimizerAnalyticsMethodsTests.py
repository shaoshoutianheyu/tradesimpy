from tests_import import *
import unittest
import pandas as pd
import market_data
import optimizer_analytics
from pprint import pprint


class OptimizerAnalyticsMethodsTests(unittest.TestCase):

	def setUp(self):
		# Initialize market data loading values
		tickers = ['SPY']
		ticker_types = ['']
		data_sources = ['CSV']
		start_date = pd.to_datetime('1993-01-29')
		end_date = pd.to_datetime('2016-5-31')
		history_window = 0
		csv_data_uri = "support_files"

		# Load market data and save for later use
		data = market_data.load_market_data(tickers, ticker_types, data_sources, start_date, end_date,
			history_window, csv_data_uri)
		self.test_series = data['SPY']['Adjusted Close']

	def test_sharpe_ratio_analytics_method(self):
		log_returns = optimizer_analytics.log_returns(self.test_series)
		sharpe_ratio = optimizer_analytics.sharpe_ratio(log_returns, 'daily')

		self.assertAlmostEqual(0.4547538253, sharpe_ratio, places=8)

	def test_sortino_ratio_analytics_method(self):
		log_returns = optimizer_analytics.log_returns(self.test_series)
		sortino_ratio = optimizer_analytics.sortino_ratio(log_returns, 'daily')

		self.assertAlmostEqual(0.5831621098, sortino_ratio, places=8)

	def test_mar_ratio_analytics_method(self):
		self.assertTrue(False, 'Not implemented!')

	def test_max_drawdown_analytics_method(self):
		self.assertTrue(False, 'Not implemented!')

	def test_var_analytics_method(self):
		self.assertTrue(False, 'Not implemented!')

	def test_cvar_analytics_method(self):
		self.assertTrue(False, 'Not implemented!')

if __name__ == '__main__':
    unittest.main()
