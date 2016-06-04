import pickle
import logging as log
from datetime import datetime


class OptimizationResults(object):

    def __init__(self, backtest_results, optimal_parameters, parameter_sets):
        self.backtest_results = backtest_results
        self.optimal_parameters = optimal_parameters
        self.parameter_sets = parameter_sets

    def save_pickle(self, file_uri):
        log.info('Storing the results...')
    	pickle.dump(self, open('%s/optimization_results_%s.p' % (file_uri, datetime.now()), "wb"))
        log.info('Results stored!')
    	print
