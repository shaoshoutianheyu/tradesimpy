
class TradingAlgorithm(object):
    def __init__(self, long_only, tickers, params):
        # Data members
        self.long_only = long_only
        self.tickers = tickers
        self.params = params
        self.is_open = False

    def set_parameters(self, params):
        self.params = params
