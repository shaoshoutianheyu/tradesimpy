from tests_import import *
import unittest
from BacktestConfiguration import BacktestConfiguration
from BacktestEngine import BacktestEngine
from Backtester import Backtester
from OptimizationConfiguration import OptimizationConfiguration
from OptimizationEngine import OptimizationEngine
from Optimizer import Optimizer
from WalkForwardAnalysisConfiguration import WalkForwardAnalysisConfiguration
from WalkForwardAnalysisEngine import WalkForwardAnalysisEngine
from WalkForwardAnalyzer import WalkForwardAnalyzer


class EngineTests(unittest.TestCase):
    def test_backtest_engine(self):
        engine = BacktestEngine()
        config = BacktestConfiguration('./support_files/correct_backtest_config.json')
        results = engine.run(config)

        # Check results
        self.assertNotEquals(len(results.cash), 0)
        self.assertNotEquals(len(results.invested), 0)
        self.assertNotEquals(len(results.fees), 0)
        self.assertNotEquals(len(results.transactions), 0)
        self.assertNotEquals(len(results.portfolio_value), 0)
        self.assertNotEquals(len(results.profit_and_loss), 0)

    def test_optimization_engine(self):
        engine = OptimizationEngine()
        config = OptimizationConfiguration('./support_files/correct_optimization_config.json')
        results = engine.run(config)

        # Check results
        self.assertNotEquals(len(results.backtest_results), 0)
        self.assertNotEquals(len(results.optimal_parameters), 0)
        self.assertNotEquals(len(results.parameter_sets), 0)

    def test_walk_forward_analysis_engine(self):
        engine = WalkForwardAnalysisEngine()
        config = WalkForwardAnalysisConfiguration('./support_files/correct_walk_forward_analysis_config.json')
        results = engine.run(config)

        # Check results
        self.assertNotEquals(len(results.optimization_results), 0)
        self.assertNotEquals(len(results.backtest_results), 0)

if __name__ == '__main__':
    unittest.main()
