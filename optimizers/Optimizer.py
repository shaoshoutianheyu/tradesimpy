from optimizer_import import *
import trading_algorithms.TradingAlgorithmFactory as taf
import OptimizerFactory as of
import DataImport as di
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
    opt_metric = configData['opt_metric']
    opt_metric_asc = bool(configData['opt_metric_asc'])
    algo_name = configData['algo_name'].lower()
    long_only = bool(configData['long_only'])
    capital_base = float(configData['capital_base'])
    commission = float(configData['commission'])
    benchmark_ticker = configData['benchmark_ticker']
    tickers_spreads = configData['tickers_spreads']
    start_date = datetime.strptime(configData['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(configData['end_date'], '%Y-%m-%d')
    opt_params = configData['opt_params']

    # Display inputted config parameters
    print '********  OPTIMIZATION CONFIGURATION PARAMETERS  ********'
    print 'Optimization method:     %s' % (opt_name)
    print 'Optimize metric:         %s' % (opt_metric)
    print 'Optimize metric ascend:  %s' % (opt_metric_asc)
    print 'Algorithm name:          %s' % (algo_name)
    print 'Long only:               %s' % (long_only)
    print 'Capital base:            %s' % (capital_base)
    print 'Commission:              %s' % (commission)
    print 'Start date:              %s' % (start_date)
    print 'End date:                %s' % (end_date)
    print 'Benchmark:               %s' % (benchmark_ticker)
    print 'Tickers & BA spread(s):'
    for key, value in tickers_spreads.iteritems():
        print '                         %s: %s' % (key, value)
    print 'Hyper parameters:'
    for key, value in opt_params.iteritems():
        print '                         %s: %s' % (key, value)
    print '*********************************************************'
    print

    # Create trading algorithm
    trading_algo = taf.create_trading_algo(algo_name=algo_name, long_only=long_only, tickers=tickers_spreads.keys())

    # Create and run optimizer
    optimizer = of.create_optimizer(opt_name=opt_name, opt_params=opt_params)
    print 'Optimizing parameter set for dates %s to %s.' % (start_date, end_date)
    start_time = time.time()
    results = optimizer.run(trading_algo=trading_algo, commission=commission, tickers_spreads=tickers_spreads,
                            start_date=start_date.date(), end_date=end_date.date())
    end_time = time.time()
    print 'Finished in-sample optimization in %f seconds.\n' % (end_time - start_time)

    # Sort optimization results
    results.sort(columns=[opt_metric], ascending=[opt_metric_asc], inplace=True)

    # Pull benchmark stats
    benchmark_stats = di.get_benchmark_comparison(benchmark_ticker=benchmark_ticker,
                                                  start_date=start_date,
                                                  end_date=end_date,
                                                  capital_base=capital_base)

    # Display benchmark results
    print 'Benchmark results:'
    print 'Total Return:    %f' % ((benchmark_stats['Portfolio Value'][-1] / benchmark_stats['Portfolio Value'][0]) - 1)
    print 'CAGR:            %f' % (benchmark_stats['CAGR'])
    print 'Max Drawdown:    %f' % (benchmark_stats['Max Drawdown'])
    print 'Sharpe Ratio:    %f' % (benchmark_stats['Sharpe Ratio'])
    print 'Sortino Ratio:   %f' % (benchmark_stats['Sortino Ratio'])
    print 'MAR Ratio:       %f\n' % (benchmark_stats['MAR Ratio'])

    # Display a plot of the top N scenarios' portfolio value from the sorted results
    top_scenarios = 10
    port_value_series = pd.DataFrame(data=benchmark_stats['Portfolio Value'].values,
                                     index=benchmark_stats['Portfolio Value'].index,
                                     columns=[benchmark_ticker])
    for i in range(0, top_scenarios):
        port_value_series[str(results.head(top_scenarios).iloc[i]['Params'])] =\
            pd.Series(results.head(top_scenarios).iloc[i]['Portfolio Value'],
                index=results.head(top_scenarios).iloc[i]['Portfolio Value'].keys())

    plot = port_value_series.plot(title='Portfolio Value of Top %d Scenarios and Benchmark' % (top_scenarios),
                                  legend=False,
                                  colormap='rainbow')
    plot.set_xlabel('Date')
    plot.set_ylabel('Porfolio Value')
    plot.legend(loc=2, prop={'size': 10})

    # Output relevant optimization results to csv file
    filename = '%s.%s.%s.csv' % (algo_name, opt_name, datetime.now())
    del results['Portfolio Value']
    results.to_csv(filename, index=False)

    print 'Top %d scenario results:' % (top_scenarios)
    print results.head(top_scenarios)[
        ['Params',
         'Total Return',
         'CAGR',
         'Max Drawdown',
         'Sharpe Ratio',
         'Sortino Ratio',
         'MAR Ratio',
         'Total Trades',
         'Winning Trades',
         'Losing Trades',
         'Average Winning Trade',
         'Average Losing Trade']
    ]
    plt.show()
