import exceptions as ex
import MovingAverageDivergenceAlgorithm

class TradingAlgorithm(object):
    def __init__(self, long_only, tickers, params):
        # Data members
        self.long_only = long_only
        self.tickers = tickers
        self.params = params
        self.is_open = False

    def set_parameters(self, params):
        self.params = params

    # TODO: Put this in a factory class
    @staticmethod
    def create_trading_algo(algo_name, long_only, tickers, params=None):
        if algo_name == 'ma_div':
            return MovingAverageDivergenceAlgorithm(long_only=long_only, tickers=tickers, params=params)
        else:
            # print 'ERROR: Unknown algo name %s' % (algo_name)
            ex.AttributeError.message('ERROR: Unknown algo name %s' % (algo_name))