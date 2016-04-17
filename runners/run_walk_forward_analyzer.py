from runner_script_import import *
import sys
from WalkForwardAnalysisConfiguration import WalkForwardAnalysisConfiguration
from WalkForwardAnalysisEngine import WalkForwardAnalysisEngine
from pprint import pprint

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please provide valid parameters {[configuration file]}')
        exit(1)

    args = sys.argv[1:]
    config_uri = args[0]

    # Create walk forward analysis configuration and display
    config = WalkForwardAnalysisConfiguration(config_uri)
    config.__str__()

    # Initialize and run the walk forward analysis engine
    walk_forward_analysis_engine = WalkForwardAnalysisEngine()
    results = walk_forward_analysis_engine.run(config)

    # Display results
    #results.print_results()

    # TODO: Store the results in a binary file
