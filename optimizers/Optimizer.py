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
    print 'Optimizing parameter set for dates %s to %s.' % (start_date, end_date)
    start_time = time.time()
    results = optimizer.run(trading_algo, start_date.date(), end_date.date())
    end_time = time.time()
    print 'Finished in-sample optimization in %f seconds.\n' % (end_time - start_time)

    # Sort optimization results
    results.sort(
        columns=['Sharpe Ratio', 'Sortino Ratio', 'Max Drawdown', 'CAGR', 'Total Trades'],
        ascending=[0, 0, 0, 0, 0],
        inplace=True)

    # Pull benchmark data, scale, and get statistics for comparison analysis
    benchmark_ticker = 'SPY'
    benchmark_data = di.load_data([benchmark_ticker], start_date, end_date, adjusted=True)[benchmark_ticker]
    benchmark_close = benchmark_data['Close'] * (capital_base / benchmark_data['Close'][0])
    benchmark_returns = (benchmark_close - benchmark_close.shift(1)) / benchmark_close.shift(1)
    benchmark_avg_returns = benchmark_returns.mean() * 252
    benchmark_std_dev = benchmark_returns.std() * np.sqrt(252)
    benchmark_semi_std_dev = benchmark_returns.where(benchmark_returns < 0.0).std() * np.sqrt(252)
    benchmark_sharpe = benchmark_avg_returns / benchmark_std_dev
    benchmark_sortino = benchmark_avg_returns / benchmark_semi_std_dev
    benchmark_cagr = (benchmark_close[-1] / benchmark_close[0]) ** (1 / ((end_date - start_date).days / 365.0)) - 1
    global_high = 0.0
    local_low = 0.0
    benchmark_max_drawdown = 0.0
    for p in benchmark_data.index:
        if benchmark_data.ix[p]['High'] > global_high:
            global_high = benchmark_data.ix[p]['High']
            local_low = global_high

        if benchmark_data.ix[p]['Low'] < local_low:
            local_low = benchmark_data.ix[p]['Low']

            # Record max drawdown
            if ((local_low / global_high) - 1) < benchmark_max_drawdown:
                benchmark_max_drawdown = (local_low / global_high) - 1

    # Display a plot of the top N scenarios' portfolio value from the sorted results
    num_scenarios = 10
    port_value_series = pd.DataFrame(benchmark_close)
    for i in range(0, num_scenarios):
        port_value_series[str(results.head(num_scenarios).iloc[i]['Params'])] =\
            pd.Series(results.head(num_scenarios).iloc[i]['Portfolio Value'],
                index=results.head(num_scenarios).iloc[i]['Portfolio Value'].keys())

    plot = port_value_series.plot(title='Portfolio Value of Top %d Scenarios and Benchmark' % (num_scenarios),
                                  legend=False,
                                  colormap='rainbow')
    plot.set_xlabel('Date')
    plot.set_ylabel('Porfolio Value')
    plot.legend(loc=2, prop={'size': 10})

    # Output relevant optimization results to csv file
    filename = '%s.%s.%s.csv' % (algo_name, opt_name, datetime.now())
    del results['Portfolio Value']
    results.to_csv(filename, index=False)

    print 'Benchmark results:'
    print 'Total Return: %f' % ((benchmark_close[-1] / benchmark_close[0]) - 1)
    print 'CAGR: %f' % (benchmark_cagr)
    print 'Max Drawdown: %f' % (-benchmark_max_drawdown)
    print 'Sharpe Ratio: %f' % (benchmark_sharpe)
    print 'Sortino Ratio: %f' % (benchmark_sortino)
    print 'MAR Ratio: %f\n' % (-benchmark_cagr / benchmark_max_drawdown)

    print 'Top %d scenario results:' % (num_scenarios)
    print results.head(num_scenarios)[
        ['Params',
         'Total Return',
         'CAGR',
         'Max Drawdown',
         'Sharpe Ratio',
         'Sortino Ratio',
         'MAR Ratio',
         'Total Trades']
    ]
    plt.show()
