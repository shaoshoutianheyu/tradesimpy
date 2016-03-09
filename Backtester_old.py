from backtester_import import *
import json
import numpy as np
import pandas as pd
import time
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
import DataImport as di
import Simulator as sim
import SystemParameters as sp
import trading_algorithms.TradingAlgorithmFactory as taf
import optimizers.OptimizerFactory as of

YEARLY_TRADE_DAYS = 252


class Backtester(object):

    def __init__(self, params):
        # Data members
        self.params = params
        self.in_sample_day_cnt = np.round(params.in_sample_year_cnt * YEARLY_TRADE_DAYS)
        self.out_sample_day_cnt = np.round(params.out_sample_year_cnt * YEARLY_TRADE_DAYS)

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
        self.sample_periods = self.create_sample_periods(self.params.start_date, self.params.end_date,
                                                         self.in_sample_day_cnt, self.out_sample_day_cnt)

        # Display sample period date ranges
        print('Sample periods:')
        for per in self.sample_periods:
            print('    In:  %s - %s (%d)' % (per['in'][0].date(), per['in'][1].date(), (per['in'][1] - per['in'][0]).days))
            print('    Out: %s - %s (%d)' % (per['out'][0].date(), per['out'][1].date(), (per['out'][1] - per['out'][0]).days))
            print

        # TODO: Pull data required for all in-sample and out-of-sample periods

    def run(self):
        portfolio_series = pd.DataFrame()
        portfolio_stats = list()
        capital_base = self.params.capital_base

        # Create trading algorithm, optimizer, and simulator
        trading_algo = taf.create_trading_algo(params=self.params)
        optimizer = of.create_optimizer(params=self.params)
        simulator = sim.Simulator(capital_base=capital_base, commission=self.params.commission,
                                  stop_loss_percent=self.params.stop_loss_percent,
                                  tickers_spreads=self.params.tickers_spreads, carry_over_trades=self.params.carry_over_trades)

        # Backtest trading algorithm
        for per in self.sample_periods:
            in_start = per['in'][0]
            in_end = per['in'][1]
            out_start = per['out'][0]
            out_end = per['out'][1]

            # Get optimal parameters based on performance metric and historical time horizon
            print('Optimizing parameter set for dates %s to %s.' % (in_start.date(), in_end.date()))
            start_time = time.time()
            # algo_params = optimizer.run(trading_algo=trading_algo, start_date=in_start, end_date=in_end)
            optimizer.run(trading_algo=trading_algo, start_date=in_start, end_date=in_end)
            end_time = time.time()
            print('Finished in-sample optimization in %f seconds.\n' % (end_time - start_time))
            algo_params = optimizer.params

            # Set trading algorithm's parameters
            trading_algo.set_parameters(params=algo_params, carry_over_trades=self.params.carry_over_trades)

            # Pull out-of-sample data
            data = di.load_data(tickers=self.params.tickers_spreads.keys(),
                                start=out_start.date(),
                                end=out_end.date(),
                                adjusted=True,
                                prev_data_size=trading_algo.hist_window)

            # Simulate over out-of-sample data
            print('Simulating algorithm for dates %s to %s.' % (out_start.date(), out_end.date()))
            start_time = time.time()
            period_results, daily_results = simulator.run(capital_base=capital_base, trading_algo=trading_algo, data=data)
            end_time = time.time()
            print('Finished out-of-sample simulation %f seconds.\n' % (end_time - start_time))

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
        print('Please provide valid parameters {[configuration file]}')
        exit(1)

    args = sys.argv[1:]
    configFile = args[0]

    # Extract data from config (JSON) file
    with open(configFile, mode='r') as f:
        configData = json.loads(f.read())

    # Set system config parameters and display
    params = sp.SystemParameters(configData)
    params.display()

    # Initialize and run backtest
    backtester = Backtester(params)
    portfolio_stats, portfolio_series = backtester.run()

    # Pull benchmark stats
    benchmark_stats = di.get_benchmark_comparison(benchmark_ticker=params.benchmark_ticker,
                                                  start_date=params.start_date,
                                                  end_date=params.end_date,
                                                  capital_base=params.capital_base)

    # Display benchmark results
    print('Benchmark results:')
    print('Total Return:        %f' % ((benchmark_stats['Portfolio Value'][-1] / benchmark_stats['Portfolio Value'][0]) - 1))
    print('Annual Volatility    %f' % (benchmark_stats['Return Std Dev']))
    print('CAGR:                %f' % (benchmark_stats['CAGR']))
    print('Max Drawdown:        %f' % (benchmark_stats['Max Drawdown']))
    print('Sharpe Ratio:        %f' % (benchmark_stats['Sharpe Ratio']))
    print('Sortino Ratio:       %f' % (benchmark_stats['Sortino Ratio']))
    print('MAR Ratio:           %f\n' % (benchmark_stats['MAR Ratio']))

    # Compute backtest stats
    # TODO: Package these computations into a library
    years_traded = ((params.end_date - params.start_date).days + 1) / 365.0
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
    print('Backtest results:')
    print('Total Return:            %f' % (backtest_total_return - 1))
    print('Annual Volatility:       %f' % (backtest_std_dev))
    print('CAGR:                    %f' % (backtest_cagr))
    print('Max Drawdown:            %f' % (portfolio_stats[-1]['Max Drawdown']))
    print('Sharpe Ratio:            %f' % (backtest_sharpe))
    print('Sortino Ratio:           %f' % (backtest_sortino))
    print('MAR Ratio:               %f' % (backtest_cagr / portfolio_stats[-1]['Max Drawdown']))
    print('Total Trades:            %d' % (backtest_total_trades))
    print('Percent Winning Trades:  %.2f' % (backtest_win_trades / float(backtest_total_trades)))
    print('Percent Losing Trades:   %.2f' % (backtest_lose_trades / float(backtest_total_trades)))
    print('Average Winning Trades:  %f' % (np.sum(backtest_avg_win_trade) / len(backtest_avg_win_trade)))
    print('Average Losing Trades:   %f' % (np.sum(backtest_avg_lose_trade) / len(backtest_avg_lose_trade)))

    # Display a plot comparing the benchmark and portfolio values
    port_value_series = pd.DataFrame(data=benchmark_stats['Portfolio Value'].values,
                                     index=benchmark_stats['Portfolio Value'].index,
                                     columns=[params.benchmark_ticker])
    port_value_series['Algorithm'] = portfolio_series['Portfolio Value']
    plot = port_value_series.plot(title='Trading Algorithm vs. Benchmark',
                                  legend=False,
                                  colormap='rainbow')
    plot.set_xlabel('Date')
    plot.set_ylabel('Value')
    plot.legend(loc=2, prop={'size': 10})
    plt.show()
