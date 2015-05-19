from backtester_import import *
import json
import numpy as np
import pandas as pd
import time
from pprint import pprint
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
import DataImport as di
import Simulator as sim
import trading_algorithms.TradingAlgorithmFactory as taf
import optimizers.OptimizerFactory as of


class Backtester(object):
    def __init__(self, opt_name, opt_metric, opt_metric_asc, algo_name, long_only, capital_base, commission,
                 tickers_spreads, start_date, end_date, in_sample_day_cnt, out_sample_day_cnt, carry_over_trades,
                 opt_params, sys_params):
        # Data members
        self.opt_name = opt_name
        self.opt_metric = opt_metric
        self.opt_metric_asc = opt_metric_asc
        self.algo_name = algo_name
        self.long_only = long_only
        self.capital_base = capital_base
        self.commission = commission
        self.tickers_spreads = tickers_spreads
        self.start_date = start_date
        self.end_date = end_date
        self.in_sample_day_cnt = in_sample_day_cnt
        self.out_sample_day_cnt = out_sample_day_cnt
        self.carry_over_trades = carry_over_trades
        self.opt_params = opt_params
        self.sys_params = sys_params

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
        portfolio_series = pd.DataFrame()
        portfolio_stats = list()
        capital_base = self.capital_base

        # Create trading algorithm, optimizer, and simulator
        trading_algo = taf.create_trading_algo(algo_name=self.algo_name, long_only=self.long_only,
                                               tickers=self.tickers_spreads.keys(), params=self.sys_params)
        optimizer = of.create_optimizer(opt_name=self.opt_name, opt_params=self.opt_params, sys_params=self.sys_params)
        simulator = sim.Simulator(capital_base=capital_base, commission=self.commission,
                                  stop_loss_percent=self.sys_params['stop_loss_percent'],
                                  tickers_spreads=tickers_spreads, carry_over_trades=self.carry_over_trades)

        # Get the trading algorithm's required window length
        req_cnt = trading_algo.hist_window

        # Backtest trading algorithm using walk forward analysis
        for periods in self.sample_periods:
            in_start = periods['in'][0]
            in_end = periods['in'][1]
            out_start = periods['out'][0]
            out_end = periods['out'][1]

            # Optimize over in-sample data
            print 'Optimizing parameter set for dates %s to %s.' % (in_start.date(), in_end.date())
            start_time = time.time()
            in_sample_results = optimizer.run(trading_algo=trading_algo, commission=self.commission,
                                              tickers_spreads=tickers_spreads, start_date=in_start, end_date=in_end)
            end_time = time.time()
            print 'Finished in-sample optimization in %f seconds.\n' % (end_time - start_time)

            # Sort the results based on performance metrics and get parameters
            in_sample_results = in_sample_results[in_sample_results['Total Trades'] >= self.sys_params['min_trades']]
            params = in_sample_results.sort(
                columns=[self.opt_metric],
                ascending=[self.opt_metric_asc]
            )['Params'].head(1).values[0]

            # Set trading algorithm's parameters
            trading_algo.set_parameters(params=params, carry_over_trades=carry_over_trades)

            # Adjust the date range to approximately accommodate for indicator window length
            data_start_date = out_start - BDay(req_cnt + 5)

            # Pull out-of-sample data
            data = di.load_data(tickers=self.tickers_spreads.keys(), start=data_start_date.date(), end=out_end.date(),
                                adjusted=True)

            # Grab only the required data
            for ticker in trading_algo.tickers:
                # Start on valid date
                while out_start not in data[ticker].index:
                    out_start += BDay(1)

                start_idx = data[ticker][:out_start][-req_cnt-1:].index.tolist()[0]
                data[ticker] = data[ticker][start_idx:]

            # Simulate over out-of-sample data
            print 'Simulating algorithm for dates %s to %s.' % (out_start.date(), out_end.date())
            start_time = time.time()
            period_results, daily_results =\
                simulator.run(capital_base=capital_base, trading_algo=trading_algo, data=data)
            end_time = time.time()
            print 'Finished out-of-sample simulation %f seconds.\n' % (end_time - start_time)

            # Keep track of the portfolio's value over time
            capital_base = period_results['End Portfolio Value']

            # Record results for later analysis
            portfolio_stats.append(period_results)

            # Concatenate all out-of-sample simulations
            portfolio_series = pd.concat([portfolio_series, daily_results[['Portfolio Value', 'Return']]])

        return portfolio_stats, portfolio_series

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
    opt_metric = configData['opt_metric']
    opt_metric_asc = bool(configData['opt_metric_asc'])
    algo_name = configData['algo_name'].lower()
    long_only = bool(configData['long_only'])
    capital_base = float(configData['capital_base'])
    commission = float(configData['commission'])
    benchmark_ticker = configData['benchmark_ticker']
    tickers_spreads = configData['tickers_spreads']
    start_date = pd.datetime.strptime(configData['start_date'], "%Y-%m-%d")
    end_date = pd.datetime.strptime(configData['end_date'], "%Y-%m-%d")
    in_sample_day_cnt = configData['in_sample_days']
    out_sample_day_cnt = configData['out_sample_days']
    carry_over_trades = bool(configData['carry_over_trades'])
    opt_params = configData['opt_params']
    hist_window = configData['hist_window']
    min_trades = configData['min_trades']
    stop_loss_percent = configData['stop_loss_percent']

    # Display inputted config parameters
    print '**********  BACKTEST CONFIGURATION PARAMETERS  **********'
    print 'Optimization method:     %s' % (opt_name)
    print 'Optimize metric:         %s' % (opt_metric)
    print 'Optimize metric ascend:  %s' % (opt_metric_asc)
    print 'Algorithm name:          %s' % (algo_name)
    print 'Long only:               %s' % (long_only)
    print 'Capital base:            %s' % (capital_base)
    print 'Commission:              %s' % (commission)
    print 'Start date:              %s' % (start_date)
    print 'End date:                %s' % (end_date)
    print 'In-sample day count:     %s' % (in_sample_day_cnt)
    print 'Out-of-sample day count: %s' % (out_sample_day_cnt)
    print 'Carry over trades:       %s' % (carry_over_trades)
    print 'Benchmark ticker:        %s' % (benchmark_ticker)
    print 'Historical window:       %s' % (hist_window)
    print 'Minimum trades:          %s' % (min_trades)
    print 'Stop loss percent:       %s' % (stop_loss_percent)
    print 'Tickers & BA spread(s):'
    for key, value in tickers_spreads.iteritems():
        print '                         %s: %s' % (key, value)
    print 'Hyper parameters:'
    for key, value in opt_params.iteritems():
        print '                         %s: %s' % (key, value)
    print '*********************************************************'
    print

    # Pass necessary parameters
    sys_params = {
        'hist_window':  hist_window,
        'min_trades':   min_trades,
        'stop_loss_percent': stop_loss_percent
    }

    # Initialize and run backtest
    backtester = Backtester(opt_name=opt_name,
                            opt_metric=opt_metric,
                            opt_metric_asc=opt_metric_asc,
                            algo_name=algo_name,
                            long_only=long_only,
                            capital_base=capital_base,
                            commission=commission,
                            tickers_spreads=tickers_spreads,
                            start_date=start_date,
                            end_date=end_date,
                            in_sample_day_cnt=in_sample_day_cnt,
                            out_sample_day_cnt=out_sample_day_cnt,
                            carry_over_trades=carry_over_trades,
                            opt_params=opt_params,
                            sys_params=sys_params)
    portfolio_stats, portfolio_series = backtester.run()

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

    # Compute backtest stats
    years_traded = ((end_date - start_date).days + 1) / 365.0
    backtest_avg_return = portfolio_series['Return'].mean() * 252
    backtest_std_dev = portfolio_series['Return'].std() * np.sqrt(252)
    backtest_semi_std_dev = portfolio_series['Return'].where(portfolio_series['Return'] < 0.0).std() * np.sqrt(252)
    backtest_sharpe = backtest_avg_return / backtest_std_dev
    backtest_sortino = backtest_avg_return / backtest_semi_std_dev
    backtest_total_return = portfolio_stats[-1]['End Portfolio Value'] / portfolio_stats[0]['Start Portfolio Value']
    backtest_cagr = backtest_total_return ** (1 / years_traded) - 1
    backtest_avg_win_trade =\
        [t['Average Winning Trade'] for t in portfolio_stats if not np.isnan(t['Average Winning Trade'])]
    backtest_avg_lose_trade =\
        [t['Average Losing Trade'] for t in portfolio_stats if not np.isnan(t['Average Losing Trade'])]
    backtest_total_trades = np.sum([t['Total Trades'] for t in portfolio_stats])
    backtest_win_trades = np.sum([t['Winning Trades'] for t in portfolio_stats])
    backtest_lose_trades = np.sum([t['Losing Trades'] for t in portfolio_stats])

    # Display backtesting results
    print 'Backtest results:'
    print 'Total Return:            %f' % (backtest_total_return - 1)
    print 'CAGR:                    %f' % (backtest_cagr)
    print 'Max Drawdown:            %f' % (portfolio_stats[-1]['Max Drawdown'])
    print 'Sharpe Ratio:            %f' % (backtest_sharpe)
    print 'Sortino Ratio:           %f' % (backtest_sortino)
    print 'MAR Ratio:               %f' % (backtest_cagr / portfolio_stats[-1]['Max Drawdown'])
    print 'Total Trades:            %d' % (backtest_total_trades)
    print 'Percent Winning Trades:  %.2f' % (backtest_win_trades / float(backtest_total_trades))
    print 'Percent Losing Trades:   %.2f' % (backtest_lose_trades / float(backtest_total_trades))
    print 'Average Winning Trades:  %f' % (np.sum(backtest_avg_win_trade) / len(backtest_avg_win_trade))
    print 'Average Losing Trades:   %f' % (np.sum(backtest_avg_lose_trade) / len(backtest_avg_lose_trade))

    # Display a plot comparing the benchmark and portfolio values
    port_value_series = pd.DataFrame(data=benchmark_stats['Portfolio Value'].values,
                                     index=benchmark_stats['Portfolio Value'].index,
                                     columns=[benchmark_ticker])
    port_value_series['Algorithm'] = portfolio_series['Portfolio Value']
    plot = port_value_series.plot(title='Trading Algorithm vs. Benchmark',
                                  legend=False,
                                  colormap='rainbow')
    plot.set_xlabel('Date')
    plot.set_ylabel('Value')
    plot.legend(loc=2, prop={'size': 10})
    plt.show()
