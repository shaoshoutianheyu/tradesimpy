from trading_algorithm_import import *
import exceptions as ex
import indicators.Indicators as ind
from MovingAverageDivergenceAlgorithm import MovingAverageDivergenceAlgorithm
#from OuterInnerWatermarkAlgorithm import OuterInnerWatermarkAlgorithm


def create_trading_algo(algorithm_name, tickers, history_window, algorithm_parameters=None):

    if algorithm_name == 'ma_div':
        return MovingAverageDivergenceAlgorithm(tickers=tickers, history_window=history_window, params=algorithm_parameters)
    #elif algo_name == 'sobel_outerinnerwatermark':
    #    return OuterInnerWatermarkAlgorithm(long_only=long_only, tickers=tickers, params=None,
    #                                        indicator=ind.sobel_operator, hist_window=config.hist_window, is_open=None)
    #elif algo_name == 'lse_angle_outerinnerwatermark':
    #    return OuterInnerWatermarkAlgorithm(long_only=long_only, tickers=tickers, params=None,
    #                                        indicator=ind.least_squares_angle, hist_window=config.hist_window, is_open=None)
    else:
        ex.AttributeError.message('ERROR: Unknown algo name %s' % (algo_name))
