from trading_algorithm_import import *
import exceptions as ex
import indicators.Indicators as ind
from OuterInnerWatermarkAlgorithm import OuterInnerWatermarkAlgorithm
from MovingAverageDivergenceAlgorithm import MovingAverageDivergenceAlgorithm


def create_trading_algo(algo_name, long_only, tickers, params=None, is_open=None):
    if algo_name == 'ma_div':
        return MovingAverageDivergenceAlgorithm(long_only=long_only, tickers=tickers, params=params, is_open=is_open)
    elif algo_name == 'sobel_outerinnerwatermark':
        return OuterInnerWatermarkAlgorithm(long_only=long_only, tickers=tickers, params=params,
                                            indicator=ind.sobel_operator, is_open=is_open)
    elif algo_name == 'lse_angle_outerinnerwatermark':
        return OuterInnerWatermarkAlgorithm(long_only=long_only, tickers=tickers, params=params,
                                            indicator=ind.least_squares_angle, is_open=is_open)
    else:
        # print 'ERROR: Unknown algo name %s' % (algo_name)
        ex.AttributeError.message('ERROR: Unknown algo name %s' % (algo_name))