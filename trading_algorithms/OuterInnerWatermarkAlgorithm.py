from TradingAlgorithm import TradingAlgorithm


class OuterInnerWatermarkAlgorithm(TradingAlgorithm):
    def __init__(self, long_only, tickers, params, indicator, is_open=None):
        super(OuterInnerWatermarkAlgorithm, self).__init__(long_only, tickers, params, is_open)

        self.indicator = indicator
        self.hist_window = params['hist_window']
        self.prev_ind_value = dict()

        for ticker in tickers:
            self.prev_ind_value[ticker] = 0

    def determine_trade_decision(self, data):
        trade_decision = dict()

        for ticker in self.tickers:
            # Compute the new indicator value
            ind_value = self.indicator(data[ticker][-self.hist_window:]['Close'], self.params)

            if self.long_only and self.prev_ind_value[ticker] != 0:
                # Decide whether or not to open a long position based on watermarks
                if not self.is_open[ticker] and ind_value < self.params['open_long']:
                    self.is_open[ticker] = True
                    trade_decision[ticker] = {'position': 1, 'portfolio_perc': 0.95/self.num_tickers}
                elif self.is_open[ticker] and ind_value > self.params['close_long']:
                    self.is_open[ticker] = False
                    trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
            elif not self.long_only and self.prev_ind_value[ticker] != 0:
                raise NotImplementedError, 'Long/short positions have not been implemented for Watermark strategies'

                # # Decide whether or not to open a long position based on watermarks
                # if not self.is_open[ticker] and ind_value < self.params['open_long']:
                #     self.is_open[ticker] = True
                #     trade_decision[ticker] = {'position': 1, 'portfolio_perc': 0.95/self.num_tickers}
                # elif self.is_open[ticker] and ind_value > self.params['close_long']:
                #     self.is_open[ticker] = False
                #     trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                #     self.long_over_short_cross = False
                # elif not self.is_open[ticker] and ind_value < self.params['open_short']:
                #     self.is_open[ticker] = True
                #     trade_decision[ticker] = {'position': -1, 'portfolio_perc': 0.95/self.num_tickers}
                # elif self.is_open[ticker] and ind_value > self.params['close_short']:
                #     self.is_open[ticker] = False
                #     trade_decision[ticker] = {'position': 0, 'portfolio_perc': 0.0}
                #     self.short_over_long_cross = False

            self.prev_ind_value[ticker] = ind_value

        return trade_decision
