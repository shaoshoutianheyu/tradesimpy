import math as m
import numpy as np
import pandas as pd
import exceptions as ex
import logging as log
from BacktestResults import BacktestResults
from TradeDecision import TradeDecision
from TradeDecisions import TradeDecisions


class Backtester(object):

    def __init__(self, backtest_id, trading_algorithm, cash, commission, ticker_spreads):
        self.backtest_id = backtest_id
        self.trading_algorithm = trading_algorithm
        self.cash = cash
        self.commission = commission
        self.ticker_spreads = ticker_spreads
        self.open_share_price = {}
        self.purchased_shares = {}
        self.prev_cash_amount = self.cash
        self.prev_invested_amount = 0.0

    def run(self, data, start_date, end_date, cash=None):
        self.data = data

        # Handle missing cash value
        if cash is not None:
            self.cash = cash
        if self.cash is None:
            self.cash = 10000

        if(self.cash <= 0):
            raise ValueError("Cash must be greater than zero.")

        # Find the tradable dates so as to include enough data to accommodate for history window
        dates = []
        for ticker in self.trading_algorithm.tickers:
            ticker_dates = self.data[ticker].index[self.trading_algorithm.history_window:]
            dates.extend(ticker_dates)
            log.info("Ticker %s will begin making trade decisions on %s" % (ticker, ticker_dates[0]))
        dates = list(set(dates))

        # Intialize daily results structures
        self.portfolio_value = {}
        self.invested_amount = {}
        self.cash_amount = {}
        self.commissions = {}
        self.transactions = {}

        # Initialize simulation results helper variables
        algo_window_length = self.trading_algorithm.history_window
        self.trade_decision = TradeDecisions()
        self.purchased_shares = {}
        self.open_share_price = {}
        self.prev_cash_amount = self.cash
        self.prev_invested_amount = 0.0

        # Iterate over all tradable days
        for date in dates:
            self.cash_amount[date] = self.prev_cash_amount
            self.invested_amount[date] = self._mark_portfolio_to_market(date)
            self.commissions[date] = 0.0
            self.transactions[date] = {}

            if(not self.trade_decision.is_empty):
                # Execute sales first to be sure cash is available for potential purchases
                if(self.trade_decision.close):
                    # Close positions
                    for trade_decision in self.trade_decision.close:
                        self._execute_transaction(date, trade_decision)
                if(self.trade_decision.open):
                    # Open positions
                    for trade_decision in self.trade_decision.open:
                        self._execute_transaction(date, trade_decision)

            # Retrieve data needed for algorithm
            algorithm_data = {}
            for ticker in self.trading_algorithm.tickers:
                # Only include data for those tickers which can trade TODAY (i.e., existing present observation)
                if(date in self.data[ticker].index):
                    algorithm_data[ticker] = self.data[ticker][:date][-algo_window_length-1:-1]
                else:
                    log.warning("Date %s is not tradable for ticker %s" % (date, ticker))

            # Remember current asset amounts for next iteration
            self.prev_cash_amount = self.cash_amount[date]
            self.prev_invested_amount = self.invested_amount[date]

            # Determine trade decisions for tomorrow's open
            self.trade_decision = self.trading_algorithm.trade_decision(algorithm_data)

        # Close all open positions after finishing the backtest
        if len(self.purchased_shares) != 0:
            temp_purchased_shares = self.purchased_shares.copy()

            for ticker, share_count in temp_purchased_shares.iteritems():
                self._execute_transaction(date, TradeDecision(ticker, 'close', position_percent=1.0))

        # Save results
        self.results = BacktestResults(self.backtest_id, self.cash_amount, self.invested_amount, self.commissions, self.transactions)

        return self.results

    def _execute_transaction(self, date, trade_decision):
        ticker = trade_decision.ticker
        ticker_idx = self.trading_algorithm.tickers.index(trade_decision.ticker)
        current_invested_amount = self._mark_portfolio_to_market(date)
        self.commissions[date] += self.commission

        if trade_decision.open_or_close == 'close':
            # Be sure there are purchased shares for the close request
            if(ticker in self.purchased_shares):
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
            total_share_count = self._determine_share_count(self.cash_amount[date], share_price, trade_decision.share_count, trade_decision.position_percent)

            # Prior to purchase, be sure enough cash is available for purchase
            if((share_price * total_share_count) > self.cash_amount[date]):
                log.warning("Cash amount %f is not enough to purchase shares at date %s" % (self.cash_amount[date], date))
                return None

            # Open position
            self.open_share_price[ticker] = share_price
            self.purchased_shares[ticker] = total_share_count
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
            raise ValueError('Both share_count and position_percent were None.')
