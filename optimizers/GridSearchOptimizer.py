import Optimizer
import itertools
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
from pprint import pprint


class GridSearchOptimizer(Optimizer):
    ind_win_fudge_factor = 5

    def __init__(self, trading_algo, param_spaces, tickers):
    # def __init__(self):
        # super(GridSearchOptimizer, self).__init__(trading_algo, param_spaces, tickers)
        super(GridSearchOptimizer, self).__init__()

        # Data members
        # self.param_sets = self.get_param_sets(self.param_spaces)
        # self.num_param_sets = len(self.param_sets)

    def run(self, trading_algo, start_date, end_date):
        all_results = list()

        # Adjust the date range to approximately accommodate for indicator window length
        data_start_date = start_date - BDay(self.trading_algo.window_length + self.ind_win_fudge_factor)

        # Load daily adjusted close financial time series data
        data = load_from_yahoo(stocks=self.tickers, indexes={}, start=data_start_date, end=end_date, adjusted=True)
        data = data.bfill()

        # Simulate all trading scenarios and save results
        for params in self.param_sets:
            # print "\nScenario parameters:"
            # for key, value in params.iteritems():
            #     print "    %s: %f" % (key, value)

            # self.tradingAlgo(startDate, self.tickers, params)
            self.tradingAlgo.set_parameters(start_date, self.tickers, params)

            # Set the trading algorithm's parameters


            # Simulate the trading algorithm
            results = self.tradingAlgo.run(data)

            # Record scenario parameters and statistics
            # TODO: Be more exact in cutting off results data frame
            all_results.append(self.extract_scenario_stats(params, results.ix[self.windowLength:]))

        return all_results

    # Generate parameter sets for each scenario
    def get_param_sets(self, param_spaces):
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
