
class Optimizer(object):

    def __init__(self, trading_algorithm, optimization_metric, optimization_metric_ascending, optimization_parameters):
        # Data members
        self.trading_algorithm = trading_algorithm
        self.optimization_metric = optimization_metric
        self.optimization_metric_ascending = optimization_metric_ascending
        self.optimization_parameters = optimization_parameters
