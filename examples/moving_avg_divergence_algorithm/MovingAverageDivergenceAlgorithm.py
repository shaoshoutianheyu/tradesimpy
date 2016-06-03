from TradingAlgorithm import TradingAlgorithm
from TradeDecisions import TradeDecisions


class MovingAverageDivergenceAlgorithm(TradingAlgorithm):

    def __init__(self, tickers, history_window, params):
        super(MovingAverageDivergenceAlgorithm, self).__init__(tickers, history_window, params)

        if params is not None:
            self.set_parameters(params)
        
        # Set support variables
        self.long_over_short_cross = False
        self.short_over_long_cross = False
        self.prev_ma_long = 0.0
        self.prev_ma_short = 0.0

    def set_parameters(self, parameters):
        TradingAlgorithm.set_parameters(self, parameters)

        self.ma_long_window = int(parameters['ma_long_window'])
        self.ma_short_window = int(parameters['ma_short_window'])
        self.open_long = parameters['open_long']
        self.close_long = parameters['close_long']
        #self.open_short = parameters['open_short']
        #self.close_short = parameters['close_short']

    def trade_decision(self, data):
        trade_decisions = TradeDecisions()

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
                if not self.position_is_open[ticker] and ma_diff > self.open_long:
                    trade_decisions.add(ticker, 'open', long_or_short='long', position_percent=0.99 / len(self.tickers))
                    self.position_is_open[ticker] = True
                elif self.position_is_open[ticker] and ma_diff < self.close_long:
                    trade_decisions.add(ticker, 'close', position_percent=0.0)
                    self.position_is_open[ticker] = False
                    self.long_over_short_cross = False
            elif self.short_over_long_cross is True:
                pass
                # Decide whether or not to open a short position
                #if not self.position_is_open[ticker] and ma_diff > self.open_short:
                #    trade_decision[ticker] = {'position': -1, 'share_count': None, 'position_percent': 0.99 / len(self.tickers)}
                #    self.position_is_open[ticker] = True
                #elif self.position_is_open[ticker] and ma_diff < self.close_short:
                #    trade_decision[ticker] = {'position': 0, 'share_count': None, 'position_percent': 0.0}
                #    self.position_is_open[ticker] = False
                #    self.short_over_long_cross = False

            self.prev_ma_long = ma_long
            self.prev_ma_short = ma_short

        return trade_decisions
