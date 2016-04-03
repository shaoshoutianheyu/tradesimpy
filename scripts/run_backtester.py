from script_import import *
import sys
from BacktestConfiguration import BacktestConfiguration
from BacktestEngine import BacktestEngine

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please provide valid parameters {[configuration file]}')
        exit(1)

    args = sys.argv[1:]
    config_uri = args[0]

    # Create backtest configuration and display
    config = BacktestConfiguration(config_uri)
    config.__str__()

    # Initialize and run the backtest engine
    backtest_engine = BacktestEngine()
    backtest_engine.run(config)

    # TODO: Retrieve backtest results and display


    # TODO: Save backtest results
