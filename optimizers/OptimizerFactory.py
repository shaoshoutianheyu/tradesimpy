from GridSearchOptimizer import GridSearchOptimizer
import exceptions as ex


def create_optimizer(opt_name, opt_params):
    if opt_name == 'grid_search':
        return GridSearchOptimizer(opt_params)
    else:
        # print 'ERROR: Unknown optimizer %s' % (optName)
        ex.AttributeError.message('ERROR: Unknown optimizer name %s' % (opt_name))