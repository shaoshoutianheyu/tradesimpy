from trading_algorithm_import import *
import exceptions as ex
import indicators.Indicators as ind
from OuterInnerWatermarkAlgorithm import OuterInnerWatermarkAlgorithm
from MovingAverageDivergenceAlgorithm import MovingAverageDivergenceAlgorithm


def create_trading_algo(params):
    algo_name = params.algo_name
    long_only = params.long_only
    tickers = params.tickers_spreads.keys()
    is_open = None

    if algo_name == 'ma_div':
        algo_params = {
                    'open_long': params.opt_params['open_long'],
                    'close_long': params.opt_params['close_long'],
                    'open_short': params.opt_params['open_short'],
                    'close_short': params.opt_params['close_short'],
                 }

        return MovingAverageDivergenceAlgorithm(long_only=long_only, tickers=tickers, params=algo_params, is_open=is_open)
    elif algo_name == 'sobel_outerinnerwatermark':
        algo_params = {
                    'open_long': params.opt_params['open_long'],
                    'close_long': params.opt_params['close_long'],
                    'delay': params.opt_params['delay'],
                    'sigma': params.opt_params['sigma'],
                 }

        return OuterInnerWatermarkAlgorithm(long_only=long_only, tickers=tickers, params=algo_params,
                                            indicator=ind.sobel_operator, hist_window=params.hist_window, is_open=is_open)
    elif algo_name == 'lse_angle_outerinnerwatermark':
        algo_params = {
                    'open_long': params.opt_params['open_long'],
                    'close_long': params.opt_params['close_long'],
                    'window': params.opt_params['window'],
                    'sigma': params.opt_params['sigma'],
                 }

        return OuterInnerWatermarkAlgorithm(long_only=long_only, tickers=tickers, params=algo_params,
                                            indicator=ind.least_squares_angle, hist_window=params.hist_window, is_open=is_open)
    else:
        ex.AttributeError.message('ERROR: Unknown algo name %s' % (algo_name))
