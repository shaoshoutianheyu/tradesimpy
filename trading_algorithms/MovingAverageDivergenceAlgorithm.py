from TradingAlgorithm import TradingAlgorithm


# TODO: Allow trading of more than one ticker
class MovingAverageDivergenceAlgorithm(TradingAlgorithm):
    def __init__(self, long_only, tickers, params):
        super(MovingAverageDivergenceAlgorithm, self).__init__(long_only, tickers, params)

        self.ma_long_window = 10
        self.ma_short_window = 2

        # Required property by all strategies
        self.hist_window_length = self.ma_long_window

    def determine_trade_decision(self, data):
        trade_decision = dict()

        for ticker in self.tickers:
            # Compute moving average difference
            ma_long = data[ticker][-self.ma_long_window:]['Close'].mean()
            ma_short = data[ticker][-self.ma_short_window:]['Close'].mean()
            ma_diff = ma_long - ma_short

            if self.long_only:
                if not self.is_open[ticker] and ma_diff > self.params['open_long']:
                    self.is_open[ticker] = True
                    trade_decision[ticker] = {'position': 1, 'portfolio_perc': 0.95/self.num_tickers}
                elif self.is_open[ticker] and ma_diff < self.params['close_long']:
                    self.is_open[ticker] = False
                    trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                # elif self.is_open and ma_diff > self.params['open_long']:
                #     # Consider monitoring position to avoid blowing up
            else:
                if not self.is_open[ticker] and ma_diff > self.params['open_long']:
                    self.is_open[ticker] = True
                    trade_decision[ticker] = {'position': 1, 'portfolio_perc': 0.95/self.num_tickers}
                elif self.is_open[ticker] and ma_diff < self.params['close_long']:
                    self.is_open[ticker] = False
                    trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                # elif self.is_open and ma_diff > self.params['open_long']:
                #     # Consider monitoring position to avoid blowing up
                elif not self.is_open[ticker] and ma_diff < self.params['open_short']:
                    self.is_open[ticker] = True
                    trade_decision[ticker] = {'position': -1, 'portfolio_perc': 0.95/self.num_tickers}
                elif self.is_open[ticker] and ma_diff > self.params['close_short']:
                    self.is_open[ticker] = False
                    trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                # elif self.is_open and ma_diff < self.params['open_short']:
                #     # Consider monitoring position to avoid blowing up

        return trade_decision
