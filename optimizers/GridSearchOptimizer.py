from Optimizer import Optimizer
import Simulator as sim
import DataImport
import itertools
import numpy as np
import pandas as pd
import multiprocessing as mp
from pandas.tseries.offsets import BDay
from pprint import pprint


def _simulation(sim_args):
    # Extract simulation arguments
    params, trading_algo, commission, stop_loss_percent, tickers_spreads, data = sim_args

    # Simulate the trading algorithm with distinct parameters
    trading_algo.set_parameters(params=params, carry_over_trades=False)
    simulator = sim.Simulator(capital_base=10000, commission=commission, stop_loss_percent=stop_loss_percent,
                              tickers_spreads=tickers_spreads, trading_algo=trading_algo, data=data)
    period_results, daily_results = simulator.run()

    # Append parameters to trading statistics and several time series
    period_results['Params'] = params
    period_results['Portfolio Value'] = daily_results['Portfolio Value']

    return period_results


class GridSearchOptimizer(Optimizer):
    ind_win_fudge_factor = 5

    # TODO: Stop loss percent should be a parameter for the underlying algorithm
    def __init__(self, param_spaces, commission, stop_loss_percent, tickers_spreads, min_trades, opt_metric, opt_metric_asc):
        super(GridSearchOptimizer, self).__init__(param_spaces)

        # Data members
        self.param_sets = self.get_param_sets(self.param_spaces)
        self.num_param_sets = len(self.param_sets)
        self.commission = commission
        self.stop_loss_percent = stop_loss_percent
        self.tickers_spreads = tickers_spreads
        self.min_trades = min_trades
        self.opt_metric = opt_metric
        self.opt_metric_asc = opt_metric_asc

    def run(self, trading_algo, start_date, end_date):
        results = []

        # Get the trading algorithm's required window length
        # TODO: hist_window needs to be relocated so algos that don't require it don't need to store it
        req_cnt = trading_algo.hist_window

        # Adjust the date range to approximately accommodate for indicator window length
        data_start_date = start_date - BDay(req_cnt + self.ind_win_fudge_factor)

        # Load daily adjusted close financial time series data
        data = DataImport.load_data(tickers=trading_algo.tickers, start=data_start_date, end=end_date, adjusted=True)

        # Grab only the required data
        for ticker in trading_algo.tickers:
            # Start on valid date
            while start_date not in data[ticker].index:
                start_date += BDay(1)

            start_idx = data[ticker][:start_date][-req_cnt:].index.tolist()[0]
            data[ticker] = data[ticker][start_idx:]

        # # Simulate all trading scenarios and save results
        # for params in self.param_sets:
        #     # print "\nScenario parameters:"
        #     # for key, value in params.iteritems():
        #     #     print "    %s: %f" % (key, value)

        #     # Set the trading algorithm's parameters
        #     trading_algo.set_parameters(params=params, carry_over_trades=False)

        #     # Simulate the trading algorithm
        #     simulator = sim.Simulator(capital_base=10000, commission=self.commission, stop_loss_percent=self.stop_loss_percent,
        #                               tickers_spreads=self.tickers_spreads, trading_algo=trading_algo, data=data)
        #     period_results, daily_results = simulator.run()

        #     # Record scenario parameters and statistics
        #     period_results['Params'] = params
        #     period_results['Portfolio Value'] = daily_results['Portfolio Value']
        #     results.append(period_results)

        # Prepare input data for running parallel simulations
        simulation_args = itertools.izip(
            self.param_sets,
            itertools.repeat(trading_algo),
            itertools.repeat(self.commission),
            itertools.repeat(self.stop_loss_percent),
            itertools.repeat(self.tickers_spreads),
            itertools.repeat(data)
        )

        # Simulate all trading scenarios in parallel
        pool = mp.Pool(processes=mp.cpu_count() / 2)
        results = pool.map(func=_simulation, iterable=simulation_args)
        results = pd.DataFrame(results)

        # Sort the results based on performance metrics and get parameters
        results = results[results['Total Trades'] >= self.min_trades]
        params = results.sort(
            columns=[self.opt_metric],
            ascending=[self.opt_metric_asc]
        )['Params'].head(1).values[0]

        self.params = params
        # return params
        return results

    # Generate parameter sets for each scenario
    # TODO: Build parameter sets based on the long_only and opt_params settings from config file
    @staticmethod
    def get_param_sets(param_spaces):
        discrete_param_spaces = []
        param_names = []
        param_sets = []

        # Discretize each parameter space
        for key, value in param_spaces.iteritems():
            # Skip unused parameters
            if len(value) == 0:
                continue

            discrete_param_spaces.append(list(np.linspace(value[0], value[1], value[2])))
            param_names.append(key)

        # Generate all unique parameter sets
        temp_param_sets = list(itertools.product(*discrete_param_spaces))

        # Build proper output structure
        for p in temp_param_sets:
            params = {}
            for i in range(0, len(p)):
                params[param_names[i]] = p[i]

            param_sets.append(params)

        return param_sets
