from TradingAlgorithm import TradingAlgorithm


class MovingAverageDivergenceAlgorithm(TradingAlgorithm):
    def __init__(self, long_only, tickers, params):
        super(MovingAverageDivergenceAlgorithm, self).__init__(long_only, tickers, params)

        self.ma_long_window = 20
        self.ma_short_window = 4

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
            else:
                if not self.is_open[ticker] and ma_diff > self.params['open_long']:
                    self.is_open[ticker] = True
                    trade_decision[ticker] = {'position': 1, 'portfolio_perc': 0.95/self.num_tickers}
                elif self.is_open[ticker] and ma_diff < self.params['close_long']:
                    self.is_open[ticker] = False
                    trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                elif not self.is_open[ticker] and ma_diff < self.params['open_short']:
                    self.is_open[ticker] = True
                    trade_decision[ticker] = {'position': -1, 'portfolio_perc': 0.95/self.num_tickers}
                elif self.is_open[ticker] and ma_diff > self.params['close_short']:
                    self.is_open[ticker] = False
                    trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}

        return trade_decision
