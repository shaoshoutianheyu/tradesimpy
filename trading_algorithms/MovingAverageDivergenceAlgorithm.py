from TradingAlgorithm import TradingAlgorithm


class MovingAverageDivergenceAlgorithm(TradingAlgorithm):

    def __init__(self, tickers, history_window, params):
        super(MovingAverageDivergenceAlgorithm, self).__init__(tickers, history_window, params)

        self.set_parameters(params)
        
        # Set support variables
        self.long_over_short_cross = False
        self.short_over_long_cross = False
        self.prev_ma_long = 0.0
        self.prev_ma_short = 0.0

    def set_parameters(self, params):
        self.ma_long_window = params['ma_long_window']
        self.ma_short_window = params['ma_short_window']
        self.open_long = params['open_long']
        self.open_short = params['close_long']

    def trade_decision(self, data):
        trade_decision = {}

        for ticker in self.tickers:
            # Compute moving average difference
            ma_long = data[ticker][-self.ma_long_window:]['Close'].mean()
            ma_short = data[ticker][-self.ma_short_window:]['Close'].mean()
            ma_diff = ma_long - ma_short

            # Monitor moving average crosses
            if self.prev_ma_long < self.prev_ma_short and ma_long > ma_short:
                self.long_over_short_cross = True
                self.short_over_long_cross = False
            elif self.prev_ma_long > self.prev_ma_short and ma_long < ma_short:
                self.long_over_short_cross = False
                self.short_over_long_cross = True

            # Only trade prior to a long-over-short or short-over-long moving average cross
            if self.long_over_short_cross is True:
                # Decide whether or not to open a long position
                if not self.position_is_open[ticker] and ma_diff > self.params['open_long']:
                    # TODO: Check for open short positions and close if they exist
                    self.close_open_positions()

                    trade_decision[ticker] = {'position': 1, 'portfolio_perc': 0.95/self.num_tickers}
                    self.position_is_open[ticker] = True
                elif self.position_is_open[ticker] and ma_diff < self.params['close_long']:
                    trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                    self.position_is_open[ticker] = False
                    self.long_over_short_cross = False
            elif self.short_over_long_cross is True:
                # Decide whether or not to open a short position
                if not self.position_is_open[ticker] and ma_diff < self.params['open_short']:
                    # TODO: Check for open long positions and close if they exist
                    self.close_open_positions()
                    
                    trade_decision[ticker] = {'position': -1, 'portfolio_perc': 0.95/self.num_tickers}
                    self.position_is_open[ticker] = True
                elif self.position_is_open[ticker] and ma_diff > self.params['close_short']:
                    trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                    self.position_is_open[ticker] = False
                    self.short_over_long_cross = False

            self.prev_ma_long = ma_long
            self.prev_ma_short = ma_short

        return trade_decision

    def close_open_positions(self):
        pass
