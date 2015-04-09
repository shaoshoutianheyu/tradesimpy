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
    params, trading_algo, data = sim_args

    # print "Scenario parameters: %r" % (params)

    # Simulate the trading algorithm with distinct parameters
    trading_algo.set_parameters(params=params)
    simulator = sim.Simulator(capital_base=100000, trading_algo=trading_algo, data=data)
    period_results, daily_results = simulator.run()

    # Append parameters to trading statistics
    period_results['Params'] = params

    return period_results


class GridSearchOptimizer(Optimizer):
    ind_win_fudge_factor = 5

    def __init__(self, param_spaces):
        super(GridSearchOptimizer, self).__init__(param_spaces)

        # Data members
        self.param_sets = self.get_param_sets(self.param_spaces)
        self.num_param_sets = len(self.param_sets)

    def run(self, trading_algo, start_date, end_date):
        results = list()

        # Get the trading algorithm's required window length
        req_cnt = trading_algo.hist_window_length

        # Adjust the date range to approximately accommodate for indicator window length
        data_start_date = start_date - BDay(req_cnt + self.ind_win_fudge_factor)

        # Load daily adjusted close financial time series data
        data = DataImport.load_data(tickers=trading_algo.tickers, start=data_start_date, end=end_date, adjusted=True)

        # Grab only the required data
        for ticker in trading_algo.tickers:
            start_idx = data[ticker][:start_date][-req_cnt:].index.tolist()[0]
            data[ticker] = data[ticker][start_idx:]

        # Simulate all trading scenarios and save results
        for params in self.param_sets:
            print "\nScenario parameters:"
            for key, value in params.iteritems():
                print "    %s: %f" % (key, value)

            # Set the trading algorithm's parameters
            trading_algo.set_parameters(params=params)

            # Simulate the trading algorithm
            simulator = sim.Simulator(capital_base=10000, trading_algo=trading_algo, data=data)
            period_results, daily_results = simulator.run()

            # pprint(daily_results)
            # for t in daily_results['Transactions']:
            #     print t
            exit(1)

            # Record scenario parameters and statistics
            period_results['Params'] = params
            results.append(period_results)

        # Prepare input data for running parallel simulations
        simulation_args = itertools.izip(
            self.param_sets,
            itertools.repeat(trading_algo),
            itertools.repeat(data),
        )

        # Simulate all trading scenarios in parallel
        pool = mp.Pool(processes=mp.cpu_count())
        results = pool.map(func=_simulation, iterable=simulation_args)

        return pd.DataFrame(results)

    # Generate parameter sets for each scenario
    # TODO: Build parameter sets based on the long_only and opt_params settings from config file
    @staticmethod
    def get_param_sets(param_spaces):
        discrete_param_spaces = list()
        param_names = list()
        param_sets = list()

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
            params = dict()
            for i in range(0, len(p)):
                params[param_names[i]] = p[i]

            param_sets.append(params)

        return param_sets
