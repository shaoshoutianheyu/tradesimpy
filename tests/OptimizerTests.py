from tests_import import *
import unittest
import pandas as pd
import market_data
from TradingAlgorithm import TradingAlgorithm
from Optimizer import Optimizer
from GridSearchOptimizer import GridSearchOptimizer
import optimizer_factory as of
from pprint import pprint


class OptimizerTests(unittest.TestCase):

	def test_grid_search_optimizer_as_expected(self):
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

		# Initialize grid search optimizer values
		algorithm_uri = "support_files/MovingAverageDivergenceAlgorithm.py"
		num_processors = 4
		commission = 0.0
		ticker_spreads = [0.0001]
		optimizer_name = "GridSearchOptimizer"
		optimization_metric = "sharpe_ratio"
		optimization_metric_ascending = True
		optimization_parameters = {
			"ma_long_window"    : [10, 20, 2],
			"ma_short_window"   : [2, 5, 2],
			"open_long"         : [-0.25, -0.25, 1],
			"close_long"        : [0.4, 0.4, 1]
		}
		time_resolution = "daily"

		# Create trading algorithm
		trading_algorithm = TradingAlgorithm.create_trading_algorithm(algorithm_uri, tickers,
			history_window, None)

		# Setup and run the optimizer
		optimizer = of.create_optimizer(num_processors, optimizer_name, trading_algorithm, commission,
			ticker_spreads, optimization_metric, optimization_metric_ascending, optimization_parameters,
			time_resolution)
		results = optimizer.run(data, start_date, end_date)

		# Manually compute optimal parameters
		opt_params = Optimizer.get_optimal_parameters(results.backtest_results, optimization_metric, results.parameter_sets,
			optimization_metric_ascending, time_resolution)

		# Check results
		self.assertEqual(opt_params, results.optimal_parameters)
		self.assertTrue(len(results.backtest_results) == len(results.parameter_sets))
		self.assertEqual(4, len(results.backtest_results))

if __name__ == '__main__':
    unittest.main()
