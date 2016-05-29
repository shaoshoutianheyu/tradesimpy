from runner_script_import import *
import sys
from OptimizationConfiguration import OptimizationConfiguration
from OptimizationEngine import OptimizationEngine

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please provide valid parameters {[configuration file]}')
        exit(1)

    args = sys.argv[1:]
    config_uri = args[0]

    # Create backtest configuration and display
    config = OptimizationConfiguration(config_uri)
    config.__str__()

    # Initialize and run the backtest engine
    optimization_engine = OptimizationEngine()
    results = optimization_engine.run(config)

    # Display results
    #results.print_results()

    # Store the results in a binary file
    print('Storing the results...')
    results.save_pickle(config.results_uri)
    print('Results stored!')
    print
