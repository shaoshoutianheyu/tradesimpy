from tests_import import *
import unittest
import sys
from TradingAlgorithm import TradingAlgorithm
from TradeDecision import TradeDecision


class TradingAlgorithmTests(unittest.TestCase):
	def test_create_trading_algorithm_module_loading(self):
		# Create trading algorithm
		algorithm_uri = './support_files/MovingAverageDivergenceAlgorithm.py'
		trading_algorithm = TradingAlgorithm.create_trading_algorithm(algorithm_uri, [], 0)

		# Check results
		self.assertTrue('MovingAverageDivergenceAlgorithm' in sys.modules)
		self.assertEquals(str(sys.modules['MovingAverageDivergenceAlgorithm']), \
			"<module 'MovingAverageDivergenceAlgorithm' from './support_files/MovingAverageDivergenceAlgorithm.pyc'>")

	def test_create_trading_algorithm_incorrect_file_extension(self):
		algorithm_uri = './support_files/MovingAverageDivergenceAlgorithm.cheez'

		with self.assertRaises(NameError):
			trading_algorithm = TradingAlgorithm.create_trading_algorithm(algorithm_uri, [], 0)

	# def test_create_trading_algorithm_incorrect_class(self):
	# 	raise NotImplementedError('This test needs work.')
	# 	# algorithm_uri = './support_files/MagicAlgorithm.py'

	# 	# with self.assertRaises(TypeError):
	# 	# 	trading_algorithm = TradingAlgorithm.create_trading_algorithm(algorithm_uri, [], 0)

	def test_trade_decision_with_correct_share_count(self):
		# __init__(self, ticker, open_or_close, long_or_short=None, share_count=None, position_percent=None):
		trade_decision = TradeDecision([], 'open', 'long', 100, None)

		# Check results
		self.assertEquals(trade_decision.share_count, 100)
		self.assertEquals(trade_decision.position_percent, None)

	def test_trade_decision_with_missing_share_count_and_position_percent(self):
		with self.assertRaises(ValueError):
			trade_decision = TradeDecision([], 'open', 'long', None, None)

	def test_trade_decision_with_correct_position_percent(self):
		trade_decision = TradeDecision([], 'open', 'long', None, 0.9)

		# Check results
		self.assertEquals(trade_decision.share_count, None)
		self.assertEquals(trade_decision.position_percent, 0.9)

	def test_trade_decision_incorrect_open_or_close(self):
		with self.assertRaises(ValueError):
			trade_decision = TradeDecision([], 'invalid', 'long', 100, None)

	def test_trade_decision_correct_close(self):
		trade_decision = TradeDecision([], 'close', 'long', 100, None)

		# Check results
		self.assertEquals(trade_decision.long_or_short, None)

	def test_trade_decision_correct_open_and_correct_long(self):
		trade_decision = TradeDecision([], 'open', 'long', 100, None)

		# Check results
		self.assertEquals(trade_decision.long_or_short, 'long')

	def test_trade_decision_correct_open_and_correct_short(self):
		trade_decision = TradeDecision([], 'open', 'short', 100, None)

		# Check results
		self.assertEquals(trade_decision.long_or_short, 'short')

	def test_trade_decision_correct_open_and_incorrect_long_or_short(self):
		with self.assertRaises(ValueError):
			trade_decision = TradeDecision([], 'open', 'invalid', 100, None)

if __name__ == '__main__':
    unittest.main()
