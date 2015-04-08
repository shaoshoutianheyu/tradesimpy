from backtester_import import *
import json
import pandas as pd
from pprint import pprint
from pandas.tseries.offsets import BDay
import DataImport as di
import Simulator as sim
import trading_algorithms.TradingAlgorithmFactory as taf
import optimizers.OptimizerFactory as of


class Backtester(object):
    def __init__(self, opt_name, algo_name, long_only, capital_base, tickers, start_date, end_date, in_sample_day_cnt,
                 out_sample_day_cnt, opt_params, display_info=False):
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
            print 'Starting in-sample optimization for dates %s to %s.\n' % (in_start.date(), in_end.date())
            in_sample_results = optimizer.run(trading_algo=trading_algo, start_date=in_start, end_date=in_end)
            print '\nFinished in-sample optimization for dates %s to %s.\n' % (in_start.date(), in_end.date())

            # Sort the results based on performance metrics and get parameters
            params = in_sample_results.sort(
                columns=['Sharpe Ratio', 'Sortino Ratio', 'Max Drawdown', 'CAGR', 'Total Trades'],
                ascending=[0, 0, 0, 0, 0]
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
            print 'Starting out-of-sample simulation for dates %s to %s.\n' % (out_start.date(), out_end.date())
            out_sample_results, junk = simulator.run(capital_base=capital_base, trading_algo=trading_algo, data=data)
            print '\nFinished out-of-sample simulation for dates %s to %s.\n' % (out_start.date(), out_end.date())

            # Keep track of the portfolio's value over time
            capital_base = out_sample_results['End Portfolio Value']

            # Record results for later analysis
            results.append(out_sample_results)

        pprint(results)

    def create_sample_periods(self, start_date, end_date, in_sample_day_cnt, out_sample_day_cnt):
        sample_periods = list()

        # Full sample period
        start_datetime = pd.datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = pd.datetime.strptime(end_date, "%Y-%m-%d")

        # Determine and store all sample periods
        while (start_datetime + BDay(out_sample_day_cnt - 1)) <= end_datetime:
            inStart = start_datetime - BDay(in_sample_day_cnt)
            inEnd = start_datetime - BDay(1)
            outStart = start_datetime
            outEnd = start_datetime + BDay(out_sample_day_cnt - 1)

            sample_periods.append(
                {
                    'in':   [inStart, inEnd],
                    'out':  [outStart, outEnd]
                }
            )

            # Update new start date
            start_datetime = start_datetime + BDay(out_sample_day_cnt)

        # Be sure to include any remaining days in full sample period as a sample period
        if start_datetime < end_datetime:
            sample_periods.append(
                {
                    'in':   [start_datetime - BDay(in_sample_day_cnt), start_datetime - BDay(1)],
                    'out':  [start_datetime, end_datetime]
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
    position_type = configData['position_type'].lower()
    capital_base = float(configData['capital_base'])
    tickers = configData['tickers']
    start_date = configData['start_date']
    end_date = configData['end_date']
    in_sample_day_cnt = int(configData['in_sample_days'])
    out_sample_day_cnt = int(configData['out_sample_days'])
    opt_params = configData['opt_params']

    # Display inputted config parameters
    print '**********  BACKTEST CONFIGURATION PARAMETERS  **********'
    print 'Optimization method:     %s' % (opt_name)
    print 'Algorithm name:          %s' % (algo_name)
    print 'Position type:           %s' % (position_type)
    print 'Capital base:            %s' % (capital_base)
    print 'Start date:              %s' % (start_date)
    print 'End date:                %s' % (end_date)
    print 'In-sample day count:     %s' % (in_sample_day_cnt)
    print 'Out-of-sample day count: %s' % (out_sample_day_cnt)
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
                            opt_params=opt_params,
                            display_info=True)
    results = backtester.run()
