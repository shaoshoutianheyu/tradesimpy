from Optimizer import Optimizer
import Simulator
import DataImport
import itertools
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
from pprint import pprint


class GridSearchOptimizer(Optimizer):
    ind_win_fudge_factor = 5

    def __init__(self, param_spaces):
        super(GridSearchOptimizer, self).__init__(param_spaces)

        # Data members
        self.param_sets = self.get_param_sets(self.param_spaces)
        self.num_param_sets = len(self.param_sets)

    def run(self, trading_algo, start_date, end_date):
        all_results = list()

        # Get the trading algorithm's required window length
        req_cnt = trading_algo.req_hist_data_cnt

        # Adjust the date range to approximately accommodate for indicator window length
        data_start_date = start_date - BDay(req_cnt + self.ind_win_fudge_factor)

        # Load daily adjusted close financial time series data
        data = DataImport.load_data(tickers=trading_algo.tickers, start=data_start_date, end=end_date, adjusted=True)
        # print data

        # # Simulate all trading scenarios and save results
        # for params in self.param_sets:
        #     print "\nScenario parameters:"
        #     for key, value in params.iteritems():
        #         print "    %s: %f" % (key, value)
        #
        #     # Set the trading algorithm's parameters
        #     trading_algo.set_parameters(params)
        #
        #     # Simulate the trading algorithm
        #     simulator = Simulator(trading_algo, start_date, end_date, data)
        #     results = simulator.run();
        #     # results = self.tradingAlgo.run(data)
        #
        #     # Record scenario parameters and statistics
        #     # TODO: Be more exact in cutting off results data frame
        #     # all_results.append(self.extract_scenario_stats(params, results.ix[self.windowLength:]))
        #
        #     print 'made it'
        #     exit(0)

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
