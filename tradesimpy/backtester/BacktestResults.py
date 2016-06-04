import pandas as pd
import numpy as np
import pickle
import logging as log
from datetime import datetime


class BacktestResults(object):

    def __init__(self, backtest_id, cash_series, invested_series, fees_series, transactions_series):
        self.backtest_id = backtest_id

        # Save base time series
        self.cash = pd.Series(cash_series.values(), cash_series.keys()).sort_index()
        self.invested = pd.Series(invested_series.values(), invested_series.keys()).sort_index()
        self.fees = pd.Series(fees_series.values(), fees_series.keys()).sort_index()
        self.transactions = pd.Series(transactions_series.values(), transactions_series.keys()).sort_index()

        # Add portfolio value series
        self.portfolio_value = pd.Series(self.cash + self.invested, cash_series.keys()).sort_index()

        # Add profit and loss series
        self.profit_and_loss = pd.Series(self.portfolio_value - self.portfolio_value.shift(1), cash_series.keys()).sort_index()

        # Add discrete returns series
        self.discrete_returns = pd.Series(self.profit_and_loss / self.portfolio_value.shift(1), cash_series.keys()).sort_index()

        # Add log returns series
        self.log_returns = pd.Series(np.log(self.portfolio_value / self.portfolio_value.shift(1)), cash_series.keys()).sort_index()

    def save_pickle(self, file_uri):
        log.info('Storing the results...')
        pickle.dump(self, open('%s/backtest_results_%s.p' % (file_uri, datetime.now()), "wb"))
        log.info('Results stored!')
        print
