
class TradingAlgorithm(object):

    def __init__(self, tickers, history_window, params):
        # Data members
        self.tickers = tickers
        self.history_window = history_window
        self.params = params

        # Initialize to no current open positions
        self.position_is_open = {}
        for ticker in self.tickers:
            self.position_is_open[ticker] = False
