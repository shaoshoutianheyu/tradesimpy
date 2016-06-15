from tests_import import *
import unittest
from BacktestConfiguration import BacktestConfiguration
from OptimizationConfiguration import OptimizationConfiguration
from WalkForwardAnalysisConfiguration import WalkForwardAnalysisConfiguration


class ConfigurationTests(unittest.TestCase):
    def test_backtest_configuration_correct_config_file(self):
        config = BacktestConfiguration('./support_files/correct_backtest_config.json')

    def test_optimization_configuration_config_file(self):
        config = OptimizationConfiguration('./support_files/correct_optimization_config.json')

    def test_walk_forward_analysis_configuration_config_file(self):
        config = WalkForwardAnalysisConfiguration('./support_files/correct_walk_forward_analysis_config.json')

if __name__ == '__main__':
    unittest.main()
