import pandas as pd
import numpy as np
from pprint import pprint


class WalkForwardAnalysisResults(object):

    def __init__(self):
        self.optimization_results = []
        self.backtest_results = []

    def add_results(self, optimization_results, backtest_results):
    	self.optimization_results.append(optimization_results)
    	self.backtest_results.append(backtest_results)

    def print_results(self):
        pass

    def save_pickle(self, file_uri):
    	pass
