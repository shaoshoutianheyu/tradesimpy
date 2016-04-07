from backtest_import import *
import math as m
import numpy as np
import pandas as pd
from pprint import pprint


class Backtester(object):

    def __init__(self, cash, commission, ticker_spreads):
        self.cash = cash
        self.start_dates = {}
        self.portfolio_global_high = cash
        self.portfolio_local_low = cash
        self.commission = commission
        self.ticker_spreads = ticker_spreads
        self.open_share_price = {}
        self.purchased_shares = {}
        self.prev_portfolio_value = self.cash
        self.prev_cash_amount = self.cash
        self.prev_invested_amount = 0.0

    def run(self, cash, trading_algo, data):
        self.data = data
        self.cash = cash
        self.trading_algo = trading_algo

        # Determine trading start dates for each ticker
        for ticker in self.trading_algo.tickers:
            self.start_dates[ticker] = self.data[ticker].index[self.trading_algo.history_window]

        # TODO: Make this more flexible for multiple tickers!
        self.dates = self.data[self.trading_algo.tickers[0]][self.start_dates[self.trading_algo.tickers[0]]:].index.tolist()

        # Intialize daily results structures
        self.portfolio_value = {}
        self.p_n_l = {}
        self.transactions = {}
        self.invested_amount = {}
        self.cash_amount = {}
        self.commissions = {}

        # Initialize simulation results helper variables
        algo_window_length = self.trading_algo.history_window
        algo_data = {}
        self.trade_decision = {}
        self.purchased_shares = {}
        self.open_share_price = {}
        self.prev_portfolio_value = self.cash
        self.prev_cash_amount = self.cash
        self.prev_invested_amount = 0.0

        # Iterate over all trading days
        for date in self.dates:
            self.cash_amount[date] = self.prev_cash_amount
            self.invested_amount[date] = self.mark_portfolio_to_market(date)
            self.commissions[date] = 0.0
            self.transactions[date] = {}

            # Execute trade decisions made during yesterday's close
            for ticker, decision in self.trade_decision.iteritems():
                if decision['position'] == 0 and ticker in self.purchased_shares.keys():  # Close existing position
                    self.execute_transaction(date=date, ticker=ticker, is_bid=True, share_count=decision['share_count'], \
                        position_percent=decision['position_percent'])
                elif decision['position'] == 1 and ticker not in self.purchased_shares.keys():  # Open long position
                    self.execute_transaction(date=date, ticker=ticker, is_bid=False, share_count=decision['share_count'], \
                        position_percent=decision['position_percent'])
                # TODO: Allow for short selling
                elif decision['position'] == -1:  # Open short position
                    pass

            # Retrieve data needed for algorithm
            for ticker in self.trading_algo.tickers:
                algo_data[ticker] = self.data[ticker][:date][-algo_window_length-1:-1]

            # Record more trade stats
            # TODO: Record OHLC of portfolio (portfolio_value is already Close), but maybe only OC makes sense
            self.portfolio_value[date] = self.cash_amount[date] + self.invested_amount[date]
            self.p_n_l[date] = self.portfolio_value[date] - self.prev_portfolio_value

            # Remember current asset amounts for next iteration
            self.prev_cash_amount = self.cash_amount[date]
            self.prev_invested_amount = self.invested_amount[date]
            self.prev_portfolio_value = self.portfolio_value[date]

            # Determine trade decisions for tomorrow's open
            self.trade_decision = self.trading_algo.trade_decision(algo_data)

        # Close all open positions after finishing the backtest
        if len(self.purchased_shares) != 0:
            temp_purchased_shares = self.purchased_shares.copy()

            for ticker, share_count in temp_purchased_shares.iteritems():
                self.execute_transaction(date=date, ticker=ticker, is_bid=True, share_count=None, position_percent=1.0)

        # Create data frame out of daily trade stats
        results = pd.DataFrame(self.portfolio_value.values(), columns=['Portfolio Value'], index=self.portfolio_value.keys())
        results['Cash'] = pd.Series(self.cash_amount.values(), index=self.cash_amount.keys())
        results['Invested'] = pd.Series(self.invested_amount.values(), index=self.invested_amount.keys())
        results['PnL'] = pd.Series(self.p_n_l.values(), index=self.p_n_l.keys())
        #results['Discrete Returns'] = pd.Series(returns.values(), index=returns.keys())
        #results['Log Returns'] = pd.Series(returns.values(), index=returns.keys())
        results['Commission'] = pd.Series(self.commissions.values(), index=self.commissions.keys())
        results['Transactions'] = pd.Series(self.transactions.values(), index=self.transactions.keys())
        results = results.sort_index()

        return results

    # TODO: MAKE SURE BUYING AND SELLING OCCURS ON THE NEXT DAY, NOT THE DAY OF THE DECISION!!!
    def execute_transaction(self, date, ticker, is_bid, share_count=None, position_percent=None):
        # TODO: Determine how many shares to transact
        if share_count is not None:
            pass
        elif position_percent is not None:
            pass
        else: # Error
            pass

        ticker_idx = self.trading_algo.tickers.index(ticker)
        current_invested_amount = self.mark_portfolio_to_market(date)
        self.commissions[date] += self.commission

        # TODO: Keep track of potential leverage!

        if is_bid: # Close position
            # TODO: Allow user to sell portions of position, currently closes entire position
            # TODO: Allow the user to specify at which time of the day to close position
            share_price = (1 - self.ticker_spreads[ticker_idx] / 2) * self.data[ticker].loc[date, 'Open']
            self.cash_amount[date] = self.prev_cash_amount + self.purchased_shares[ticker] * share_price - self.commission
            self.invested_amount[date] = current_invested_amount - self.purchased_shares[ticker] * share_price
            self.transactions[date][ticker] = {
                'position': 0,
                'share_count': self.purchased_shares[ticker],
                'share_price': share_price
            }
            del self.purchased_shares[ticker]
        else:   # Open position
            # TODO: Allow the user to specify at which time of the day to open position
            share_price = (1 + self.ticker_spreads[ticker_idx] / 2) * self.data[ticker].loc[date, 'Open']
            self.open_share_price[ticker] = share_price
            self.purchased_shares[ticker] = m.floor(self.prev_portfolio_value / share_price * position_percent)
            #self.purchased_shares[ticker] = share_count
            self.cash_amount[date] = self.prev_cash_amount - self.purchased_shares[ticker] * share_price - self.commission
            self.invested_amount[date] = self.prev_invested_amount + self.purchased_shares[ticker] * self.data[ticker].loc[date, 'Close']
            self.transactions[date][ticker] = {
                'position': 1,
                'share_count': self.purchased_shares[ticker],
                'share_price': share_price
            }

    def mark_portfolio_to_market(self, date):
        if len(self.purchased_shares) != 0:
            invested_amount = 0
            temp_purchased_shares = self.purchased_shares.copy()

            # Determine current invested amount
            for ticker, share_count in temp_purchased_shares.iteritems():
                invested_amount += share_count * self.data[ticker].loc[date, 'Close']

            return invested_amount
        else:
            return 0.0
