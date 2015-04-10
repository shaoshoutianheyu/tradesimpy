from backtester_import import *
import json
import numpy as np
import pandas as pd
import time
from pprint import pprint
from pandas.tseries.offsets import BDay
import DataImport as di
import Simulator as sim
import trading_algorithms.TradingAlgorithmFactory as taf
import optimizers.OptimizerFactory as of


class Backtester(object):
    def __init__(self, opt_name, algo_name, long_only, capital_base, tickers, start_date, end_date, in_sample_day_cnt,
                 out_sample_day_cnt, carry_over_trades, opt_params, display_info=False):
        # Data members
        self.opt_name = opt_name
        self.algo_name = algo_name
        self.long_only = long_only
        self.capital_base = capital_base
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.in_sample_day_cnt = in_sample_day_cnt
        self.out_sample_day_cnt = out_sample_day_cnt
        self.carry_over_trades = carry_over_trades
        self.opt_params = opt_params
        self.display_info = display_info

        # TODO: Check if ticker(s) existed during period needed for backtesting
        # for ticker in tickers:
        #     sec = symbol("SPY")
            # if sec.security_start_date > startDate:
            #     print 'ERROR: %s started trading %d and the backtest requires data up to %s' % \
            #           (sec.security_start_date, startDate)
            #
            # print '%s:          %s' % (sec.symbol, sec.security_start_date)
            # print 'Backtest:    %s' % (startDate)

        # Create list of date ranges for in-sample and out-of-sample periods
        self.sample_periods = self.create_sample_periods(start_date, end_date, in_sample_day_cnt, out_sample_day_cnt)

        if display_info:
            # Display sample period date ranges
            print 'Sample periods:'
            for sp in self.sample_periods:
                print '    In:  %s - %s (%d)' %\
                      (sp['in'][0].date(), sp['in'][1].date(), (sp['in'][1] - sp['in'][0]).days)
                print '    Out: %s - %s (%d)' %\
                      (sp['out'][0].date(), sp['out'][1].date(), (sp['out'][1] - sp['out'][0]).days)
                print

        # TODO: Pull data required for all in-sample and out-of-sample periods

        # if display_info:
        #     # Display total number of optimizations per time step
        #     print 'There will be %d distinct scenarios per optimization step\n' % (self.optimizer.num_param_sets)

    def run(self):
        results = list()
        capital_base = self.capital_base

        # Create trading algorithm, optimizer, and simulator
        trading_algo = taf.create_trading_algo(algo_name=self.algo_name, long_only=self.long_only, tickers=self.tickers)
        optimizer = of.create_optimizer(opt_name=self.opt_name, opt_params=self.opt_params)
        simulator = sim.Simulator(capital_base=capital_base)

        # Backtest trading algorithm using walk forward analysis
        for periods in self.sample_periods:
            in_start = periods['in'][0]
            in_end = periods['in'][1]
            out_start = periods['out'][0]
            out_end = periods['out'][1]

            # Optimize over in-sample data
            print 'Optimizing parameter set for dates %s to %s.' % (in_start.date(), in_end.date())
            start_time = time.time()
            in_sample_results = optimizer.run(trading_algo=trading_algo, start_date=in_start, end_date=in_end)
            end_time = time.time()
            print 'Finished in-sample optimization in %f seconds.\n' % (end_time - start_time)

            # Sort the results based on performance metrics and get parameters
            params = in_sample_results.sort(
                # columns=['Sharpe Ratio'],
                # ascending=[False]
                # columns=['Sortino Ratio'],
                # ascending=[False]
                columns=['MAR Ratio'],
                ascending=[False]
            )['Params'].head(1).values[0]

            # Set trading algorithm's parameters
            trading_algo.set_parameters(params)

            # Get the trading algorithm's required window length
            req_cnt = trading_algo.hist_window_length

            # Adjust the date range to approximately accommodate for indicator window length
            data_start_date = out_start - BDay(req_cnt + 5)

            # Pull out-of-sample data
            data = di.load_data(tickers=self.tickers, start=data_start_date, end=out_end.date(), adjusted=True)

            # Simulate over out-of-sample data
            print 'Simulating algorithm for dates %s to %s.' % (out_start.date(), out_end.date())
            start_time = time.time()
            out_sample_results, junk = simulator.run(capital_base=capital_base, trading_algo=trading_algo, data=data)
            end_time = time.time()
            print 'Finished out-of-sample simulation %f seconds.\n' % (end_time - start_time)

            # Keep track of the portfolio's value over time
            capital_base = out_sample_results['End Portfolio Value']

            # Record results for later analysis
            results.append(out_sample_results)

        return results

    def create_sample_periods(self, start_date, end_date, in_sample_day_cnt, out_sample_day_cnt):
        sample_periods = list()

        # Determine and store all sample periods
        while (start_date + BDay(out_sample_day_cnt - 1)) <= end_date:
            inStart = start_date - BDay(in_sample_day_cnt)
            inEnd = start_date - BDay(1)
            outStart = start_date
            outEnd = start_date + BDay(out_sample_day_cnt - 1)

            sample_periods.append(
                {
                    'in':   [inStart, inEnd],
                    'out':  [outStart, outEnd]
                }
            )

            # Update new start date
            start_date = start_date + BDay(out_sample_day_cnt)

        # Be sure to include any remaining days in full sample period as a sample period
        if start_date < end_date:
            sample_periods.append(
                {
                    'in':   [start_date - BDay(in_sample_day_cnt), start_date - BDay(1)],
                    'out':  [start_date, end_date]
                }
            )

        return sample_periods

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
    long_only = bool(configData['long_only'])
    capital_base = float(configData['capital_base'])
    tickers = configData['tickers']
    start_date = pd.datetime.strptime(configData['start_date'], "%Y-%m-%d")
    end_date = pd.datetime.strptime(configData['end_date'], "%Y-%m-%d")
    in_sample_day_cnt = configData['in_sample_days']
    out_sample_day_cnt = configData['out_sample_days']
    carry_over_trades = bool(configData['carry_over_trades'])
    opt_params = configData['opt_params']

    # Display inputted config parameters
    print '**********  BACKTEST CONFIGURATION PARAMETERS  **********'
    print 'Optimization method:     %s' % (opt_name)
    print 'Algorithm name:          %s' % (algo_name)
    print 'Long only:               %s' % (long_only)
    print 'Capital base:            %s' % (capital_base)
    print 'Start date:              %s' % (start_date)
    print 'End date:                %s' % (end_date)
    print 'In-sample day count:     %s' % (in_sample_day_cnt)
    print 'Out-of-sample day count: %s' % (out_sample_day_cnt)
    print 'Carry over trades:       %s' % (carry_over_trades)
    print 'Ticker(s):'
    for ticker in tickers:
        print '                         %s' % (ticker)
    print 'Hyper parameters:'
    for key, value in opt_params.iteritems():
        print '                         %s: %s' % (key, value)
    print '*********************************************************'
    print

    # Initialize and run backtester
    backtester = Backtester(opt_name=opt_name,
                            algo_name=algo_name,
                            long_only=long_only,
                            capital_base=capital_base,
                            tickers=tickers,
                            start_date=start_date,
                            end_date=end_date,
                            in_sample_day_cnt=in_sample_day_cnt,
                            out_sample_day_cnt=out_sample_day_cnt,
                            carry_over_trades=carry_over_trades,
                            opt_params=opt_params,
                            display_info=True)
    results = backtester.run()
    # pprint(results)

    # TODO: Display benchmark results

    # Compute backtest statistics
    years_traded = ((end_date - start_date).days + 1) / 365.0
    backtest_avg_sharpe =\
        np.nansum([s['Sharpe Ratio'] for s in results]) / np.count_nonzero(~np.isnan([s['Sharpe Ratio'] for s in results]))
    backtest_avg_sortino =\
        np.nansum([s['Sortino Ratio'] for s in results]) / np.count_nonzero(~np.isnan([s['Sortino Ratio'] for s in results]))
    backtest_total_return = results[-1]['End Portfolio Value'] / results[0]['Start Portfolio Value']
    backtest_cagr = backtest_total_return ** (1 / years_traded) - 1
    total_trades = np.sum([t['Total Trades'] for t in results])

    print 'Backtest results:'
    print 'Total Return:            %f' % (backtest_total_return - 1)
    print 'CAGR:                    %f' % (backtest_cagr)
    print 'Max Drawdown:            %f' % (results[-1]['Max Drawdown'])
    print 'Average Sharpe Ratio:    %f' % (backtest_avg_sharpe)
    print 'Average Sortino Ratio:   %f' % (backtest_avg_sortino)
    print 'MAR Ratio:               %f' % (backtest_cagr / results[-1]['Max Drawdown'])
    print 'Total Trades:            %d' % (total_trades)
