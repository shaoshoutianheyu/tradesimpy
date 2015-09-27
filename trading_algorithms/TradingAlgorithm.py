class TradingAlgorithm(object):

    def __init__(self, long_only, tickers, params, is_open=None):
        # Data members
        self.long_only = long_only
        self.tickers = tickers
        self.num_tickers = len(tickers)
        self.params = params

        if is_open is None:
            self.is_open = dict()

            for ticker in self.tickers:
                self.is_open[ticker] = False
        else:
            self.is_open = is_open

    def set_parameters(self, params, carry_over_trades):
        self.params = params

        # Remove memory of previous trade period's positions (if necessary)
        if not carry_over_trades:
            for ticker in self.tickers:
                self.is_open[ticker] = False
