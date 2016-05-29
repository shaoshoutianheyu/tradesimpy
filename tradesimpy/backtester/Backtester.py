from backtest_import import *
import math as m
import numpy as np
import pandas as pd
import exceptions as ex
from BacktestResults import BacktestResults


class Backtester(object):

    def __init__(self, backtest_id, trading_algorithm, cash, commission, ticker_spreads):
        self.backtest_id = backtest_id
        self.trading_algorithm = trading_algorithm
        self.cash = cash
        self.start_dates = {}
        self.commission = commission
        self.ticker_spreads = ticker_spreads
        self.open_share_price = {}
        self.purchased_shares = {}
        self.prev_cash_amount = self.cash
        self.prev_invested_amount = 0.0

    def run(self, data, cash=None):
        self.data = data

        # Handle missing cash value
        if cash is not None:
            self.cash = cash
        if self.cash is None:
            self.cash = 10000

        # Determine trading start dates for each ticker
        for ticker in self.trading_algorithm.tickers:
            self.start_dates[ticker] = self.data[ticker].index[self.trading_algorithm.history_window]

        # TODO: Make this more flexible for multiple tickers!
        self.dates = self.data[self.trading_algorithm.tickers[0]][self.start_dates[self.trading_algorithm.tickers[0]]:].index.tolist()

        # Intialize daily results structures
        self.portfolio_value = {}
        self.invested_amount = {}
        self.cash_amount = {}
        self.commissions = {}
        self.transactions = {}

        # Initialize simulation results helper variables
        algo_window_length = self.trading_algorithm.history_window
        algo_data = {}
        self.trade_decision = {}
        self.purchased_shares = {}
        self.open_share_price = {}
        self.prev_cash_amount = self.cash
        self.prev_invested_amount = 0.0

        # Iterate over all trading days
        for date in self.dates:
            self.cash_amount[date] = self.prev_cash_amount
            self.invested_amount[date] = self._mark_portfolio_to_market(date)
            self.commissions[date] = 0.0
            self.transactions[date] = {}

            # Execute trade decisions made during yesterday's close
            for ticker, decision in self.trade_decision.iteritems():
                if decision['position'] == 0 and ticker in self.purchased_shares.keys():  # Close existing position
                    self._execute_transaction(date=date, ticker=ticker, close_position=True, share_count=decision['share_count'], \
                        position_percent=decision['position_percent'])
                elif decision['position'] == 1 and ticker not in self.purchased_shares.keys():  # Open long position
                    self._execute_transaction(date=date, ticker=ticker, close_position=False, share_count=decision['share_count'], \
                        position_percent=decision['position_percent'])
                # TODO: Allow for short selling
                elif decision['position'] == -1:  # Open short position
                    pass
                    #self._execute_transaction(date=date, ticker=ticker, close_position=False, share_count=-decision['share_count'], \
                    #    position_percent=-decision['position_percent'])

            # Retrieve data needed for algorithm
            for ticker in self.trading_algorithm.tickers:
                algo_data[ticker] = self.data[ticker][:date][-algo_window_length-1:-1]

            # Remember current asset amounts for next iteration
            self.prev_cash_amount = self.cash_amount[date]
            self.prev_invested_amount = self.invested_amount[date]

            # Determine trade decisions for tomorrow's open
            self.trade_decision = self.trading_algorithm.trade_decision(algo_data)

        # Close all open positions after finishing the backtest
        if len(self.purchased_shares) != 0:
            temp_purchased_shares = self.purchased_shares.copy()

            for ticker, share_count in temp_purchased_shares.iteritems():
                self._execute_transaction(date=date, ticker=ticker, close_position=True, share_count=None, position_percent=1.0)

        # Save results
        self.results = BacktestResults(self.backtest_id, self.cash_amount, self.invested_amount, self.commissions, self.transactions)

        return self.results

    def _execute_transaction(self, date, ticker, close_position, share_count=None, position_percent=None):
        ticker_idx = self.trading_algorithm.tickers.index(ticker)
        current_invested_amount = self._mark_portfolio_to_market(date)
        self.commissions[date] += self.commission

        # TODO: Keep track of potential leverage

        if close_position:
            # TODO: Allow user to sell portions of position, currently closes entire position
            share_price = (1 - self.ticker_spreads[ticker_idx] / 2) * self.data[ticker].loc[date, 'Open']
            self.cash_amount[date] = self.prev_cash_amount + (self.purchased_shares[ticker] * share_price) - self.commission
            self.invested_amount[date] = current_invested_amount - (self.purchased_shares[ticker] * share_price)
            self.transactions[date][ticker] = {
                'position': 0,
                'share_count': self.purchased_shares[ticker],
                'share_price': share_price
            }
            del self.purchased_shares[ticker]
        else:
            share_price = (1 + self.ticker_spreads[ticker_idx] / 2) * self.data[ticker].loc[date, 'Open']
            self.open_share_price[ticker] = share_price
            self.purchased_shares[ticker] = self._determine_share_count(self.cash_amount[date], share_price, share_count, position_percent)
            self.cash_amount[date] = self.prev_cash_amount - (self.purchased_shares[ticker] * share_price) - self.commission
            self.invested_amount[date] = self.prev_invested_amount + (self.purchased_shares[ticker] * self.data[ticker].loc[date, 'Close'])
            self.transactions[date][ticker] = {
                'position': 1,
                'share_count': self.purchased_shares[ticker],
                'share_price': share_price
            }

    def _mark_portfolio_to_market(self, date):
        if len(self.purchased_shares) != 0:
            invested_amount = 0
            temp_purchased_shares = self.purchased_shares.copy()

            # Determine current invested amount
            for ticker, share_count in temp_purchased_shares.iteritems():
                invested_amount += share_count * self.data[ticker].loc[date, 'Close']

            return invested_amount
        else:
            return 0.0

    def _determine_share_count(self, leftover_cash, share_price, share_count, position_percent):
        if share_count is not None:
            return share_count
        elif position_percent is not None:
            return m.floor((leftover_cash / share_price) * position_percent)
        else:
            ex.AttributeError.message('ERROR: Both share_count and position_percent were None.')
