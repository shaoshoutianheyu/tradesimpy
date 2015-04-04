import json
import pandas as pd
from pandas.tseries.offsets import BDay
import exceptions as ex
from backtester_import import *
# from TradingAlgorithm import *
from Optimizer import *


class Backtester(object):
    def __init__(self, opt_name, algo_name, position_type, tickers, start_date, end_date, in_sample_day_cnt,
                 out_sample_day_cnt, opt_params, display_info=False):
        # Data members
        self.opt_name = opt_name
        self.algo_name = algo_name
        self.position_type = position_type
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

        # Determine position type (long only or long-short)
        if position_type == 'long_only':
            long_only = True
        else:
            long_only = False

        # Create trading algorithm
        # self.trading_algo = TradingAlgorithm.create_trading_algo(algo_name)
        self.trading_algo = self.create_trading_algo(algo_name=algo_name, long_only=long_only)

        # Create optimizer
        self.optimizer = Optimizer.create_optimizer(opt_name, opt_params, self.trading_algo)

        if display_info:
            # Display total number of optimizations per time step
            print 'There will be %d distinct scenarios per optimization step\n' % (self.optimizer.num_param_sets)

    def run(self):
        # Backtest trading algorithm using walk forward analysis
        for periods in self.sample_periods:
            in_start = periods['in'][0]
            in_end = periods['in'][1]
            out_start = periods['out'][0]
            out_end = periods['out'][1]

            # Optimize over in-sample data
            print 'Starting in-sample optimization for dates %s to %s.\n' % (in_start.date(), in_end.date())
            in_sample_results = self.optimizer.run(self.trading_algo, in_start, in_end)
            print '\nFinished in-sample optimization for dates %s to %s.\n' % (in_start.date(), in_end.date())
            # print in_sample_results

            # Simulate over out-of-sample data
            print 'Starting out-of-sample simulation for dates %s to %s.\n' % (out_start.date(), out_end.date())

            print '\nFinished out-of-sample simulation for dates %s to %s.\n' % (out_start.date(), out_end.date())

            # Record results for later analysis


            break

    # TODO: Put this in a factory class
    def create_trading_algo(self, algo_name, long_only):
        if algo_name == 'ma_div':
            return None
        else:
            # print 'ERROR: Unknown algo name %s' % (algo_name)
            ex.AttributeError.message('ERROR: Unknown algo name %s' % (algo_name))

    def create_sample_periods(self, start_date, end_date, in_sample_day_cnt, out_sample_day_cnt):
        sample_periods = list()

        # Full sample period
        startDateTime = pd.datetime.strptime(start_date, "%Y-%m-%d")
        endDateTime = pd.datetime.strptime(end_date, "%Y-%m-%d")

        # Determine and store all sample periods
        while (startDateTime + BDay(out_sample_day_cnt - 1)) <= endDateTime:
            inStart = startDateTime - BDay(in_sample_day_cnt)
            inEnd = startDateTime - BDay(1)
            outStart = startDateTime
            outEnd = startDateTime + BDay(out_sample_day_cnt - 1)

            sample_periods.append(
                {
                    'in':   [inStart, inEnd],
                    'out':  [outStart, outEnd]
                }
            )

            # Update new start date
            startDateTime = startDateTime + BDay(out_sample_day_cnt)

        # Be sure to include any remaining days in full sample period as a sample period
        if startDateTime < endDateTime:
            sample_periods.append(
                {
                    'in':   [startDateTime - BDay(in_sample_day_cnt), startDateTime - BDay(1)],
                    'out':  [startDateTime, endDateTime]
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

    # Initialize and run backtester
    backtester = Backtester(opt_name=opt_name,
                            algo_name=algo_name,
                            position_type=position_type,
                            tickers=tickers,
                            start_date=start_date,
                            end_date=end_date,
                            in_sample_day_cnt=in_sample_day_cnt,
                            out_sample_day_cnt=out_sample_day_cnt,
                            opt_params=opt_params,
                            display_info=True)
    backtester.run()
