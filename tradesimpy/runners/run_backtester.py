from runner_script_import import *
import sys
from BacktestConfiguration import BacktestConfiguration
from BacktestEngine import BacktestEngine

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise StandardError('Please provide valid parameters {[configuration file]}')

    args = sys.argv[1:]
    config_uri = args[0]

    # Create backtest configuration and display
    config = BacktestConfiguration(config_uri)
    config.__str__()

    # Initialize and run the backtest engine
    backtest_engine = BacktestEngine()
    results = backtest_engine.run(config)

    # Store the results in a binary file
    results.save_pickle(config.results_uri)
