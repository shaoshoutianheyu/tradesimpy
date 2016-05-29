from TradingAlgorithm import TradingAlgorithm
import operator
import numpy as np


class StrategicAllocationAlgorithm(TradingAlgorithm):

    def __init__(self, long_only, tickers, params, ticker_weights_range, std_dev_preference, return_resolution, is_open=None):
        super(StrategicAllocationAlgorithm, self).__init__(long_only, tickers, params, is_open)

        self.optimal_weights = {}
        self.ticker_weights_range = ticker_weights_range
        self.std_dev_preference = std_dev_preference
        self.return_resolution = return_resolution
        self.hist_window = 0

    def get_target_return_space(self, ticker_returns):
        # Take into account the minimum holdings
        required_weight = 0.0
        required_ret = 0.0
        for ticker, ret in ticker_returns.iteritems():
            min_weight = self.ticker_weight_ranges[ticker][0]
            required_weight = required_weight + min_weight
            required_ret = required_ret + (min_weight * ret)

        # Disallow invalid minimum holdings weight
        if(min_weight > 1):
            print("The minimum holdings weight cannot exceed 100%.")
            exit(1)

        # Order ascending returns
        ticker_returns_asc = sorted(ticker_returns.items(), key=operator.itemgetter(1), reverse=False)

        # Determine minimum return
        min_return = required_ret
        total_weight = required_weight
        for ticker_and_ret in ticker_returns_asc:
            max_weight = self.ticker_weight_ranges[ticker_and_ret[0]][1]
            ret = ticker_and_ret[1]
            total_weight = total_weight + max_weight

            if(total_weight >= 1 and (total_weight - max_weight) < 1):
                max_weight = max_weight - total_weight + 1
                min_return = min_return + (max_weight * ret)
                break
            else:
                min_return = min_return + (max_weight * ret)

        # Order descending returns
        ticker_returns_desc = sorted(ticker_returns.items(), key=operator.itemgetter(1), reverse=True)

        # Determine maximum return
        max_return = required_ret
        total_weight = required_weight
        for ticker_and_ret in ticker_returns_desc:
            max_weight = self.ticker_weight_ranges[ticker_and_ret[0]][1]
            ret = ticker_and_ret[1]
            total_weight = total_weight + max_weight

            if(total_weight >= 1 and (total_weight - max_weight) < 1):
                max_weight = max_weight - total_weight + 1
                max_return = max_return + (max_weight * ret)
                break
            else:
                max_return = max_return + (max_weight * ret)

        # Determine number of portfolios and target return space
        num_portfolios = int(np.ceil(((max_return - min_return) / self.return_resolution) + 1))
        target_returns = np.linspace(min_return, max_return, num_portfolios)

        return target_returns, num_portfolios

    def get_ef_portfolios(self, portfolio_weights, returns, std_devs):
        # Find the global risk minimum of the given portfolios
        min_idx = np.argmin(std_devs)
        num_portfolios = len(portfolio_weights)

        ef_portfolio_weights = portfolio_weights[min_idx:num_portfolios]
        ef_returns = returns[min_idx:num_portfolios]
        ef_std_devs = std_devs[min_idx:num_portfolios]

        return ef_portfolio_weights, ef_returns, ef_std_devs

    # TODO: If std dev target is out of range, choose closest values or something
    def get_risk_target_portfolio(self, target_std_dev, std_devs, portfolio_weights):
        # Target risk must be within risk range
        if(target_std_dev < std_devs[0] or target_std_dev > std_devs[-1]):
            print("The risk target (%f) must be within the given risk range (%f - %f)." % (target_std_dev, std_devs[0], std_devs[-1]))
            exit(1)

        # Find portfolio with given risk target
        if target_std_dev in std_devs:
            # Get index of existing element
            idx = np.where(std_devs == target_std_dev)
            target_weights = portfolio_weights[idx]
        else:
            # Find lower and upper bound indices
            lower_bound_idx = 0
            upper_bound_idx = 0
            for i in range(len(std_devs)):
                if(std_devs[i] > target_std_dev):
                    lower_bound_idx = i - 1
                    upper_bound_idx = i
                    break

            # Interpolate piecewise linearly between weight boundaries
            alpha = (target_std_dev - std_devs[lower_bound_idx]) / (std_devs[upper_bound_idx] - std_devs[lower_bound_idx])
            target_weights = ((1 - alpha) * portfolio_weights[lower_bound_idx, :]) + (alpha * portfolio_weights[upper_bound_idx, :])

        return target_weights
