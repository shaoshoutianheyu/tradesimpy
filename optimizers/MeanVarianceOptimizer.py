from Optimizer import Optimizer
import DataImport
import numpy as np
import cvxopt as opt
import pandas as pd
from pandas.tseries.offsets import BDay
# from pprint import pprint


class MeanVarianceOptimizer(Optimizer):

    def __init__(self, param_spaces, sys_params):
        super(MeanVarianceOptimizer, self).__init__(param_spaces)

        # Data members
        self.param_spaces = param_spaces
        self.sys_params = sys_params

    def run(self, trading_algo, start_date, end_date):
        results = list()
        min_ticker_weight = 0.05
        num_portfolios = self.param_spaces['num_portfolios']

        # Load daily adjusted close financial time series data
        data = DataImport.load_data(tickers=trading_algo.tickers,
                                    start=start_date,
                                    end=end_date,
                                    adjusted=True)

        # Take the log returns of all ticker data
        num_tickers = len(trading_algo.tickers)
        num_days = len(data[trading_algo.tickers[0]])
        return_data = np.ndarray((num_tickers, num_days-1))
        for i in range(num_tickers):
            temp = [data[trading_algo.tickers[i]]['Close'][j] / data[trading_algo.tickers[i]]['Close'][j-1] for j in range(1, num_days)]
            return_data[i, :] = np.log(temp)

        # Determine annual returns per ticker
        annual_returns = 252*np.mean(return_data, axis=1)

        # Set appropriate target returns range
        max_ticker_weight = 1.0 - min_ticker_weight * (num_tickers - 1)
        max_annual_return = (annual_returns.max() * max_ticker_weight) + np.sum(min_ticker_weight * annual_returns) - (min_ticker_weight * annual_returns.max())
        min_annual_return = annual_returns.min() * max_ticker_weight + np.sum(min_ticker_weight * annual_returns) - (min_ticker_weight * annual_returns.min())
        if min_annual_return < 0.0:
            min_annual_return = 0.0
        target_returns = np.linspace(min_annual_return, max_annual_return, num_portfolios)

        # Covariance matrix (objective function)
        cov = np.cov(return_data)
        Q = opt.matrix(cov)
        p = opt.matrix(0.0, (num_tickers, 1))

        # Long-only portfolio
        G = -opt.matrix(np.eye(num_tickers))
        h = -opt.matrix(min_ticker_weight, (num_tickers, 1))

        # Porfolio summed weights and returns are one and target return, respectively
        A = opt.matrix([[1.0, annual_returns[i]] for i in range(num_tickers)])

        # Compute optimal portfolios (i.e., minimum variance) per target return
        mean_variance_std_dev = np.ndarray(num_portfolios)
        mean_variance_weights = np.ndarray((num_portfolios, num_tickers))
        for i in range(num_portfolios):
            b = opt.matrix([1.0, target_returns[i]])
            sol = opt.solvers.qp(Q, p, G, h, A, b)
            mean_variance_weights[i, :] = np.array(sol['x'])[:, 0]
            mean_variance_std_dev[i] = np.sqrt(252) * np.sqrt(mean_variance_weights[i, :].T.dot(cov.dot(mean_variance_weights[i, :])))

        # Extract the efficient frontier
        ef = []
        ef.append(mean_variance_std_dev[-1])
        prev_std_dev = mean_variance_std_dev[-1]
        for i in range(2, num_portfolios+1):
            if mean_variance_std_dev[-i] > prev_std_dev:
                break

            ef.append(mean_variance_std_dev[-i])
            prev_std_dev = mean_variance_std_dev[-i]

        mean_variance_ef = np.array(ef)

        results = None

        return pd.DataFrame(results)
