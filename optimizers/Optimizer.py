import numpy as np
import json
import exceptions as ex
from optimizer_import import *
import TradingAlgorithm


class Optimizer(object):
    # def __init__(self, trading_algo, param_spaces, tickers):
    def __init__(self, param_spaces):
        # Data members
        # self.trading_algo = trading_algo
        self.param_spaces = param_spaces
        # self.tickers = tickers

    def extract_scenario_stats(self, params, results):
        record = dict()

        # Save parameters
        record['params'] = params

        # Save final portfolio value
        record['portfolio_value'] = results.portfolio_value.values[-1]

        # Save total number of positions
        tradeCount = 0
        for v in results.transactions.values:
            if v:
                tradeCount += 1
        record['position_count'] = np.ceil(tradeCount / 2.0)

        # Save Sharpe ratio
        record['sharpe_ratio'] = (np.mean(results.returns.values) / np.std(results.returns.values)) * np.sqrt(252)

        return record

    # TODO: Put this in a factory class
    @staticmethod
    def create_optimizer(opt_name, opt_params, trading_algo):
        if opt_name == 'grid_search':
            return GridSearchOptimizer(trading_algo, opt_params)
        else:
            # print 'ERROR: Unknown optimizer %s' % (optName)
            ex.AttributeError.message('ERROR: Unknown optimizer name %s' % (opt_name))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Please provide valid parameters {[configuration file]}'
        exit(1)

        args = sys.argv[1:]
        configFile = args[0]

        # Extract data from config (JSON) file
        with open(configFile, mode='r') as f:
            configData = json.loads(f.read())

        # Read in config parameters
        opt_name = configData['opt_method'].lower()
        algo_name = configData['algo_name'].lower()
        position_type = configData['position_type'].lower()
        tickers = configData['tickers']
        start_date = configData['start_date']
        end_date = configData['end_date']
        opt_params = configData['opt_params']

        # Display inputted config parameters
        print '********  OPTIMIZATION CONFIGURATION PARAMETERS  ********'
        print 'Optimization method:     %s' % (opt_name)
        print 'Algorithm name:          %s' % (algo_name)
        print 'Position type:           %s' % (position_type)
        print 'Start date:              %s' % (start_date)
        print 'End date:                %s' % (end_date)
        print 'Ticker(s):'
        for ticker in tickers:
            print '                         %s' % (ticker)
        print 'Hyper parameters:'
        for key, value in opt_params.iteritems():
            print '                         %s: %s' % (key, value)
        print '*********************************************************'
        print

    # Determine position type (long only or long-short)
    if position_type == 'long_only':
        long_only = True
    else:
        long_only = False

    # Create trading algorithm
    trading_algo = TradingAlgorithm.create_trading_algorithm(algo_name=algo_name, long_only=long_only, tickers=tickers)

    # Create and run optimizer
    optimizer = Optimizer.create_optimizer(opt_name=opt_name, opt_params=opt_params, trading_algo=trading_algo)
    optimizer.run()