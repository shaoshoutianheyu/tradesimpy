from analytics import compute_optimizer_metric
import multiprocessing as mp
import numpy as np
import operator


class Optimizer(object):

    def __init__(self, num_processors, trading_algorithm, optimization_metric, optimization_metric_ascending,
        optimization_parameters):

        if(num_processors > mp.cpu_count()):
            self.num_processors = mp.cpu_count()
        else:
            self.num_processors = num_processors

        self.trading_algorithm = trading_algorithm
        self.optimization_metric = optimization_metric
        self.optimization_metric_ascending = optimization_metric_ascending
        self.optimization_parameters = optimization_parameters

    @staticmethod
    def get_optimal_parameters(backtest_results, optimization_metric, optimization_parameter_sets, ascending, frequency):
        sorted_idices = Optimizer.get_sorted_optimal_indices(backtest_results, len(backtest_results), \
            optimization_metric, ascending, frequency)
        return optimization_parameter_sets[sorted_idices[0]]

    @staticmethod
    def get_top_n_optimal_results(backtest_results, num_results, optimization_metric, ascending, frequency):
        sorted_idices = Optimizer.get_sorted_optimal_indices(backtest_results, num_results, optimization_metric, \
            ascending, frequency)
        return [backtest_results[i] for i in sorted_idices]

    @staticmethod
    def get_sorted_optimal_indices(backtest_results, num_results, optimization_metric, ascending, frequency):
        # Compute the optimization metric per backtest result
        optimization_metrics = np.ndarray(len(backtest_results))
        for result in backtest_results:
            optimization_metrics[result.backtest_id] = compute_optimizer_metric.compute_optimizer_metric(optimization_metric, \
                result, frequency)

        # Sort optimizations metrics and save their indices
        sorted_idices = []
        if(ascending):
            sorted_idices = [i[0] for i in sorted(enumerate(optimization_metrics), key=operator.itemgetter(1))]
        else:
            sorted_idices = [i[0] for i in sorted(enumerate(optimization_metrics), key=operator.itemgetter(1), reverse=True)]

        return [sorted_idices[i] for i in range(num_results)]