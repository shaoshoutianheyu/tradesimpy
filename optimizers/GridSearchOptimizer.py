from Optimizer import Optimizer
import Backtester as b
import DataImport
import itertools
import numpy as np
import pandas as pd
import multiprocessing as mp
from pandas.tseries.offsets import BDay
from pprint import pprint


def _backtest(backtest_args):
    # Extract backtest arguments
    parameters, trading_algorithm, commission, ticker_spreads, data = backtest_args

    # Setup the trading algorithm and backtester
    trading_algorithm.set_parameters(parameters=parameters)
    backtester = b.Backtester(cash=10000, commission=commission, ticker_spreads=ticker_spreads)

    return backtester.run(trading_algorithm=trading_algorithm, data=data)

class GridSearchOptimizer(Optimizer):

    def __init__(self, trading_algorithm, commission, ticker_spreads, optimization_metric,
        optimization_metric_ascending, optimization_parameters):
        super(GridSearchOptimizer, self).__init__(trading_algorithm, optimization_metric,
            optimization_metric_ascending, optimization_parameters)

        # Data members
        self.commission = commission
        self.ticker_spreads = ticker_spreads
        self.optimization_parameter_sets = self.get_param_sets(self.optimization_parameters)
        self.num_paramameter_sets = len(self.optimization_parameter_sets)

    def run(self, data):
        # Backtest all trading scenarios and save results
        #results = []
        #for parameters in self.optimization_parameter_sets:
        #    # Set the trading algorithm's parameters
        #    self.trading_algorithm.set_parameters(parameters=parameters)

        #    # Backtest the trading algorithm
        #    backtester = b.Backtester(cash=10000, commission=self.commission, ticker_spreads=self.ticker_spreads)
        #    backtest_results = backtester.run(trading_algorithm=self.trading_algorithm, data=data)

        #    results.append(backtest_results)

        # Prepare input data for running parallel backtests
        backtest_args = itertools.izip(
            self.optimization_parameter_sets,
            itertools.repeat(self.trading_algorithm),
            itertools.repeat(self.commission),
            itertools.repeat(self.ticker_spreads),
            itertools.repeat(data)
        )

        # Run all backtest scenarios in parallel
        pool = mp.Pool(processes=mp.cpu_count())
        results = pool.map(func=_backtest, iterable=backtest_args)
        #results = pd.DataFrame(pool_results)

        # Sort the results based on performance metrics and get parameters
        # results = results[results['Total Trades'] >= self.min_trades]
        # params = results.sort(
        #     columns=[self.opt_metric],
        #     ascending=[self.opt_metric_asc]
        # )['Params'].head(1).values[0]

        # TODO: Build out analytics to map here
        # test = results.sort(
        #     columns=[self.opt_metric],
        #     ascending=[self.opt_metric_asc]
        # ).head(1).values[0]

        # pprint(test)
        # exit(0)

        # Save optimal parameters
        self.params = None
        # self.params = params

        return results

    # Generate parameter sets for each scenario
    @staticmethod
    def get_param_sets(parameter_spaces):
        discrete_param_spaces = []
        param_names = []
        param_sets = []

        # Discretize each parameter space
        for key, value in parameter_spaces.iteritems():
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
