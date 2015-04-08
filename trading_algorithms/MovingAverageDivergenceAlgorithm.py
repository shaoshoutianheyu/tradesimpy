from TradingAlgorithm import TradingAlgorithm


class MovingAverageDivergenceAlgorithm(TradingAlgorithm):
    def __init__(self, long_only, tickers, params):
        super(MovingAverageDivergenceAlgorithm, self).__init__(long_only, tickers, params)

        self.ma_long_window = 10
        self.ma_short_window = 2
        self.long_over_short_cross = False
        self.short_over_long_cross = False
        self.prev_ma_long = 0.0
        self.prev_ma_short = 0.0

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
                # Monitor moving average crosses
                if self.prev_ma_long < self.prev_ma_short and ma_long > ma_short:
                    self.long_over_short_cross = True

                # Only trade prior to a long-over-short moving average cross
                if self.long_over_short_cross == True:
                    # Decide whether or not to open a long position
                    if not self.is_open[ticker] and ma_diff > self.params['open_long']:
                        self.is_open[ticker] = True
                        trade_decision[ticker] = {'position': 1, 'portfolio_perc': 0.95/self.num_tickers}
                    elif self.is_open[ticker] and ma_diff < self.params['close_long']:
                        self.is_open[ticker] = False
                        trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                        self.long_over_short_cross = False
            else:
                # Monitor moving average crosses
                if self.prev_ma_long < self.prev_ma_short and ma_long > ma_short:
                    self.long_over_short_cross = True
                    self.short_over_long_cross = False
                elif self.prev_ma_long > self.prev_ma_short and ma_long < ma_short:
                    self.long_over_short_cross = False
                    self.short_over_long_cross = True

                # Only trade prior to a long-over-short or short-over-long moving average cross
                if self.long_over_short_cross == True:
                    # Decide whether or not to open a long position
                    if not self.is_open[ticker] and ma_diff > self.params['open_long']:
                        self.is_open[ticker] = True
                        trade_decision[ticker] = {'position': 1, 'portfolio_perc': 0.95/self.num_tickers}
                    elif self.is_open[ticker] and ma_diff < self.params['close_long']:
                        self.is_open[ticker] = False
                        trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                        self.long_over_short_cross = False
                elif self.short_over_long_cross == True:
                    # Decide whether or not to open a short position
                    if not self.is_open[ticker] and ma_diff < self.params['open_short']:
                        self.is_open[ticker] = True
                        trade_decision[ticker] = {'position': -1, 'portfolio_perc': 0.95/self.num_tickers}
                    elif self.is_open[ticker] and ma_diff > self.params['close_short']:
                        self.is_open[ticker] = False
                        trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                        self.short_over_long_cross = False

            self.prev_ma_long = ma_long
            self.prev_ma_short = ma_short

        # # Reset previous values
        # self.prev_ma_long = 0.0
        # self.prev_ma_short = 0.0

        return trade_decision
