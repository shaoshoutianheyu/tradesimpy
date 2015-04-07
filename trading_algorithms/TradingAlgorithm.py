class TradingAlgorithm(object):
    def __init__(self, long_only, tickers, params):
        # Data members
        self.long_only = long_only
        self.tickers = tickers
        self.num_tickers = len(tickers)
        self.params = params
        self.is_open = dict()

        for ticker in self.tickers:
            self.is_open[ticker] = False

    def set_parameters(self, params):
        self.params = params

        for ticker in self.tickers:
            self.is_open[ticker] = False
