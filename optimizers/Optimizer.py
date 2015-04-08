from optimizer_import import *
import trading_algorithms.TradingAlgorithmFactory as taf
import OptimizerFactory as of
import json
from datetime import datetime
from pprint import pprint

class Optimizer(object):
    def __init__(self, param_spaces):
        # Data members
        self.param_spaces = param_spaces

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
    capital_base = float(configData['capital_base'])
    tickers = configData['tickers']
    start_date = datetime.strptime(configData['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(configData['end_date'], '%Y-%m-%d')
    opt_params = configData['opt_params']

    # Display inputted config parameters
    print '********  OPTIMIZATION CONFIGURATION PARAMETERS  ********'
    print 'Optimization method:     %s' % (opt_name)
    print 'Algorithm name:          %s' % (algo_name)
    print 'Position type:           %s' % (position_type)
    print 'Capital base:            %s' % (capital_base)
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
    trading_algo = taf.create_trading_algo(algo_name=algo_name, long_only=long_only, tickers=tickers)

    # Create and run optimizer
    optimizer = of.create_optimizer(opt_name=opt_name, opt_params=opt_params)
    results = optimizer.run(trading_algo, start_date, end_date)

    # # Sort optimization results
    # results.sort(
    #     columns=['Sharpe Ratio', 'Sortino Ratio', 'Max Drawdown', 'CAGR', 'Total Trades'],
    #     ascending=[0, 0, 0, 0, 0],
    #     inplace=True)
    pprint(results)

    # Output optimization results to csv file
    filename = '%s.%s.%s.csv' % (algo_name, opt_name, datetime.now())
    results.to_csv(filename, index=False)

    print 'Finished optimization!'
