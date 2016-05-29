from StrategicAllocationAlgorithm import StrategicAllocationAlgorithm


class CVaRPortfolioAllocationAlgorithm(StrategicAllocationAlgorithm):

    def __init__(self, long_only, tickers, params, ticker_weights_range, std_dev_preference, return_resolution, is_open=None):
        super(CVaRPortfolioAllocationAlgorithm, self).__init__(long_only, tickers, params, ticker_weights_range, std_dev_preference, return_resolution, is_open)

    def determine_trade_decision(self, data):
        # Find optimal portfolio if not already done
        if not self.optimal_weights:
            self.optimal_weights = self.get_optimal_mean_cvar_portfolio(data)

        # TODO: Keep track of current allocation so as to reduce commissions when rebalancing
        trade_decision = {}
        for ticker in self.tickers:
            # Make sure all allocations have been initialized
            if not self.is_open[ticker]:
                trade_decision[ticker] = {'position': 1, 'portfolio_perc': self.optimal_weights[ticker]}
                self.is_open[ticker] = True

            # TODO: Check if rebalance threshold has been broken and rebalance if necessary

        return trade_decision

    def get_optimal_mean_cvar_portfolio(self, data):
        # self.ticker_weights_range, self.confidence_level, self.std_dev_preference, self.return_resolution
        optimal_weights = {}
        for ticker in self.tickers:
            optimal_weights[ticker] = 1.0 / len(self.tickers)

        return optimal_weights
