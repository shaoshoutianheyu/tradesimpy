import numpy as np


class Optimizer(object):
    def __init__(self, trading_algo, param_spaces, tickers):
        # Data members
        self.trading_algo = trading_algo
        self.param_spaces = param_spaces
        self.tickers = tickers

    def extract_scenario_stats(self, params, results):
        record = dict()

        # Save parameters
        record['params'] = params

        # Save final portfolio value
        record['portfolio_value'] = results.portfolio_value.values[-1]

        # Save total number of positions
        tradeCount = 0
        for v in results.transactions.values:
            if v:
                tradeCount += 1
        record['position_count'] = np.ceil(tradeCount / 2.0)

        # Save Sharpe ratio
        record['sharpe_ratio'] = (np.mean(results.returns.values) / np.std(results.returns.values)) * np.sqrt(252)

        return record