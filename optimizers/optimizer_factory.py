from GridSearchOptimizer import GridSearchOptimizer
import exceptions as ex


def create_optimizer(num_processors, optimizer_name, trading_algorithm, commission, ticker_spreads, optimization_metric,
    optimization_metric_ascending, optimization_parameters):
    optimizer_name = optimizer_name.lower()

    if optimizer_name == 'gridsearchoptimizer':
        return GridSearchOptimizer(num_processors=num_processors, trading_algorithm=trading_algorithm,
            commission=commission, ticker_spreads=ticker_spreads, optimization_metric=optimization_metric,
            optimization_metric_ascending=optimization_metric_ascending, optimization_parameters=optimization_parameters)
    else:
        ex.AttributeError.message('ERROR: Unknown optimizer name %s' % (optimizer_name))
