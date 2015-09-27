from GridSearchOptimizer import GridSearchOptimizer
# from MeanVarianceOptimizer import MeanVarianceOptimizer
import exceptions as ex


def create_optimizer(params):
    opt_name = params.opt_name

    if opt_name == 'grid_search':
        return GridSearchOptimizer(
            param_spaces=params.opt_params,
            commission=params.commission,
            stop_loss_percent=params.stop_loss_percent,
            tickers_spreads=params.tickers_spreads,
            min_trades=params.min_trades,
            opt_metric=params.opt_metric,
            opt_metric_asc=params.opt_metric_asc)
    elif opt_name == 'mean_variance':
        pass
        # return MeanVarianceOptimizer(opt_params, sys_params)
    elif opt_name == 'mean_var':
        pass
    elif opt_name == 'mean_cvar':
        pass
    else:
        ex.AttributeError.message('ERROR: Unknown optimizer name %s' % (opt_name))
