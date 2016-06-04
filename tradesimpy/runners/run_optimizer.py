from runner_script_import import *
import sys
from OptimizationConfiguration import OptimizationConfiguration
from OptimizationEngine import OptimizationEngine

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise AttributeError('Please provide valid parameters {[configuration file]}')

    args = sys.argv[1:]
    config_uri = args[0]

    # Create backtest configuration and display
    config = OptimizationConfiguration(config_uri)
    config.__str__()

    # Initialize and run the backtest engine
    optimization_engine = OptimizationEngine()
    results = optimization_engine.run(config)

    # Store the results in a binary file
    results.save_pickle(config.results_uri)
