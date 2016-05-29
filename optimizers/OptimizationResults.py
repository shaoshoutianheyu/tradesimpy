import pickle
from datetime import datetime


class OptimizationResults(object):

    def __init__(self, backtest_results, optimal_parameters, parameter_sets):
        self.backtest_results = backtest_results
        self.optimal_parameters = optimal_parameters
        self.parameter_sets = parameter_sets

    def print_results(self):
        pass

    def save_pickle(self, file_uri):
        pickle.dump(self, open('%s/optimization_results_%s.p' % (file_uri, datetime.now()), "wb"))
