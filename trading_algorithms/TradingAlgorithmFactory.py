from MovingAverageDivergenceAlgorithm import MovingAverageDivergenceAlgorithm
import exceptions as ex


def create_trading_algo(algo_name, long_only, tickers, params=None, is_open=None):
    if algo_name == 'ma_div':
        return MovingAverageDivergenceAlgorithm(long_only=long_only,
                                                tickers=tickers,
                                                params=params,
                                                is_open=is_open)
    else:
        # print 'ERROR: Unknown algo name %s' % (algo_name)
        ex.AttributeError.message('ERROR: Unknown algo name %s' % (algo_name))