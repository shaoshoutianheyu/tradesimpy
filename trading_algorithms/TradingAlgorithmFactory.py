from trading_algorithm_import import *
import exceptions as ex
import indicators.Indicators as ind
from MovingAverageDivergenceAlgorithm import MovingAverageDivergenceAlgorithm
from OuterInnerWatermarkAlgorithm import OuterInnerWatermarkAlgorithm
from CVaRPortfolioAllocationAlgorithm import CVaRPortfolioAllocationAlgorithm


def create_trading_algo(params):
    algo_name = params.algo_name
    long_only = params.long_only
    tickers = params.tickers_spreads.keys()

    if algo_name == 'ma_div':
        return MovingAverageDivergenceAlgorithm(long_only=long_only, tickers=tickers, params=None, is_open=None)
    elif algo_name == 'sobel_outerinnerwatermark':
        return OuterInnerWatermarkAlgorithm(long_only=long_only, tickers=tickers, params=None,
                                            indicator=ind.sobel_operator, hist_window=params.hist_window, is_open=None)
    elif algo_name == 'lse_angle_outerinnerwatermark':
        return OuterInnerWatermarkAlgorithm(long_only=long_only, tickers=tickers, params=None,
                                            indicator=ind.least_squares_angle, hist_window=params.hist_window, is_open=None)
    elif algo_name == 'mean_cvar_strategic_allocation':
        return CVaRPortfolioAllocationAlgorithm(long_only=long_only, tickers=tickers, params=None,
                                                ticker_weights_range=params.ticker_weights_range,
                                                std_dev_preference=params.std_dev_preference,
                                                return_resolution=params.return_resolution, is_open=None)
    else:
        ex.AttributeError.message('ERROR: Unknown algo name %s' % (algo_name))
