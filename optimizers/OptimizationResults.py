import pandas as pd
import numpy as np
from pprint import pprint


class OptimizationResults(object):

    def __init__(self, backtest_results, optimal_parameters):
        self.backtest_results = backtest_results
        self.optimal_parameters = optimal_parameters

    def print_results(self):
        pass
