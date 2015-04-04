import TradingAlgorithm
import pandas as pd


# TODO: Allow trading of more than one ticker
class MovingAverageDivergenceAlgorithm(TradingAlgorithm):
    def __init__(self, long_only, tickers, params):
        super(MovingAverageDivergenceAlgorithm, self).__init__(long_only, tickers, params)

        self.ma_long_window = 100
        self.ma_short_window = 20

        # Required property by all strategies
        self.req_hist_data_cnt = self.ma_long_window

    def determine_trade_decision(self, data):
        # Compute moving average difference
        ma_long = data[self.tickers[0]][-self.ma_long_window:].mean()
        ma_short = data[self.tickers[0]][-self.ma_short_window:].mean()
        ma_diff = ma_long - ma_short

        if self.long_only:
            if not self.is_open and ma_diff > self.params['open_long']:
                self.is_open = True
                trade_decision = {'position': 1, 'portfolio_perc': 0.95}
            elif self.is_open and ma_diff < self.params['close_long']:
                self.is_open = False
                trade_decision = {'position': 0, 'portfolio_perc': 0.0}
            elif self.is_open and ma_diff > self.params['open_long']:
                # Consider monitoring position to avoid blowing up
                trade_decision = {'position': None, 'portfolio_perc': 0.0}
        else:
            if not self.is_open and ma_diff > self.params['open_long']:
                self.is_open = True
                trade_decision = {'position': 1, 'portfolio_perc': 0.95}
            elif self.is_open and ma_diff < self.params['close_long']:
                self.is_open = False
                trade_decision = {'position': 0, 'portfolio_perc': 0.0}
            elif self.is_open and ma_diff > self.params['open_long']:
                # Consider monitoring position to avoid blowing up
                trade_decision = {'position': None, 'portfolio_perc': 0.0}
            elif not self.is_open and ma_diff < self.params['open_short']:
                self.is_open = True
                trade_decision = {'position': -1, 'portfolio_perc': 0.95}
            elif self.is_open and ma_diff > self.params['close_short']:
                self.is_open = False
                trade_decision = {'position': 0, 'portfolio_perc': 0.0}
            elif self.is_open and ma_diff < self.params['open_short']:
                # Consider monitoring position to avoid blowing up
                trade_decision = {'position': None, 'portfolio_perc': 0.0}

        return trade_decision
