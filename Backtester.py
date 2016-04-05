from backtest_import import *
import math as m
import numpy as np
import pandas as pd
# from pprint import pprint


class Backtester(object):

    def __init__(self, cash, commission, ticker_spreads):
        self.cash = cash
        self.start_dates = {}
        self.portfolio_global_high = cash
        self.portfolio_local_low = cash
        #self.max_drawdown = 0.0
        self.commission = commission
        self.ticker_spreads = ticker_spreads
        self.open_share_price = {}
        self.purchased_shares = {}
        self.prev_portfolio_value = self.cash
        self.prev_cash_amount = self.cash
        self.prev_invested_amount = 0.0

    def run(self, cash, trading_algo, data):
        self.cash = cash
        winning_trade_cnt = 0
        losing_trade_cnt = 0
        winning_trade_returns = []
        losing_trade_returns = []

        # Set trading algorithm
        self.trading_algo = trading_algo

        # Load data if necessary
        if data is not None:
            self.data = data

            # Determine trading start dates for each ticker
            for ticker in self.trading_algo.tickers:
                self.start_dates[ticker] = data[ticker].iloc[self.trading_algo.hist_window].name

            # TODO: Make this more flexible for multiple tickers!
            self.dates =\
                data[self.trading_algo.tickers[0]][self.start_dates[self.trading_algo.tickers[0]]:].index.tolist()

        # Intialize daily results structures
        self.portfolio_value = {}
        self.p_n_l = {}
        #self.returns = {}
        self.transactions = {}
        self.invested_amount = {}
        self.cash_amount = {}
        self.commissions = {}

        # Initialize simulation results helper variables
        algo_window_length = self.trading_algo.history_window
        algo_data = {}
        self.purchased_shares = {}
        self.prev_portfolio_value = self.cash
        self.prev_cash_amount = self.cash
        self.prev_invested_amount = 0.0
        self.open_share_price = {}

        # Iterate over all trading days
        for date in self.dates:
            self.cash_amount[date] = 0.0
            self.invested_amount[date] = 0.0
            self.commissions[date] = 0.0
            self.transactions[date] = {}

            # Retrieve data needed for algorithm
            for ticker in self.trading_algo.tickers:
                algo_data[ticker] = self.data[ticker][:date][-algo_window_length-1:-1]

            # Determine the trade decision for entire portfolio
            trade_desc = self.trading_algo.trade_decision(algo_data)

            # Trade off of all trade decisions
            if len(trade_desc) != 0:
                for ticker, decision in trade_desc.iteritems():
                #for key, value in trade_desc.iteritems():
                    # Close existing position
                    if decision['position'] == 0 and ticker in self.purchased_shares.keys():
                        #current_invested_amount = self.mark_portfolio_to_market()
                        # Mark the portfolio to market
                        #current_invested_amount = 0.0
                        #for k, v in self.purchased_shares.iteritems():
                        #    current_invested_amount += v*self.data[k].loc[date, 'Open']

                        # Determine at which share price to sell
                        # TODO: Introduce slippage here, set from config file
                        #share_price = self.determine_share_price(is_bid=True, is_open_price=True)
                        #share_price = (1 - self.ticker_spreads[key]/2) * self.data[key].loc[date, 'Open']

                        # Record commission
                        #commissions[date] += self.commission

                        # Sell shares for cash
                        #cash_amount[date] = self.prev_cash_amount + self.purchased_shares[key]*share_price - self.commission

                        # End of day invested amount
                        #invested_amount[date] = current_invested_amount - self.purchased_shares[key]*share_price

                        # Record transaction
                        #transactions[date][key] = {
                        #    'position': 0,
                        #    'share_count': self.purchased_shares[key],
                        #    'share_price': share_price
                        #

                        # Wining or losing trade
                        #if share_price > self.open_share_price[key]:
                        #    winning_trade_cnt += 1
                        #    winning_trade_returns.append((share_price / self.open_share_price[key]) - 1)
                        #else:
                        #    losing_trade_cnt += 1
                        #    losing_trade_returns.append((share_price / self.open_share_price[key]) - 1)

                        # Remove purchased record
                        #del self.purchased_shares[key]

                        self.execute_transaction(date=date, ticker=ticker, is_bid=True, share_count=decision['share_count'], \
                            position_percent=decision['position_percent'])

                    elif decision['position'] == 1 and ticker not in self.purchased_shares.keys():  # Open long position
                        # Determine at which share price to buy
                        # TODO: Introduce slippage here, set from config file
                        #share_price = self.determine_share_price(is_bid=False, is_open_price=True)
                        #share_price = (1 + self.ticker_spreads[key]/2) * self.data[key].loc[date, 'Open']
                        #self.purchased_shares[key] =\
                        #    m.floor(self.prev_portfolio_value/share_price*value['portfolio_perc'])

                        # Record commission
                        #commissions[date] += self.commission

                        # Purchase shares using cash
                        #cash_amount[date] = self.prev_cash_amount - self.purchased_shares[key]*share_price - self.commission

                        # End of day invested amount
                        #invested_amount[date] = self.prev_invested_amount + self.purchased_shares[key]*self.data[key].loc[date, 'Close']

                        # Record transaction
                        #transactions[date][key] = {
                        #    'position': 1,
                        #    'share_count': self.purchased_shares[key],
                        #    'share_price': share_price
                        #}
                        #elf.open_share_price[key] = share_price

                        self.execute_transaction(date=date, ticker=ticker, is_bid=False, share_count=decision['share_count'], \
                            position_percent=decision['position_percent'])

                    # TODO: Allow for short selling
                    elif decision['position'] == -1:  # Open short position
                        pass
                        # # Determine how many shares to purchase
                        # # TODO: Introduce slippage here, set from config file
                        # share_price = (1 - self.bid_ask_spread[key]/2) * self.data[key].loc[date, 'Open']
                        # purchased_shares[key] = -m.floor(prev_portfolio_value/share_price*value['portfolio_perc'])
                        #
                        # # Record commission
                        # commissions[date] += self.commission
                        #
                        # # Purchase shares using cash
                        # cash_amount[date] = prev_cash_amount - purchased_shares[key]*share_price - self.commission
                        #
                        # # End of day invested amount
                        # invested_amount[date] =\
                        #     prev_invested_amount + purchased_shares[key]*self.data[key].loc[date, 'Close']
                        #
                        # # Record transaction
                        # transactions[date][key] = {
                        #     'position': -1,
                        #     'share_count': purchased_shares[key],
                        #     'share_price': share_price
                        # }
                    else:  # No trades
                        cash_amount[date] = self.prev_cash_amount
                        invested_amount[date] = self.mark_portfolio_to_market()

            else:  # No trades
                cash_amount[date] = self.prev_cash_amount
                invested_amount[date] = self.mark_portfolio_to_market()

            # Record more trade stats
            self.portfolio_value[date] = self.cash_amount[date] + self.invested_amount[date]
            self.p_n_l[date] = self.portfolio_value[date] - self.prev_portfolio_value
            #self.returns[date] = (self.portfolio_value[date] / self.prev_portfolio_value) - 1.0

            # Remember current asset amounts for next iteration
            self.prev_cash_amount = self.cash_amount[date]
            self.prev_invested_amount = self.invested_amount[date]
            self.prev_portfolio_value = self.portfolio_value[date]

            # Monitor portfolio drawdown (conservatively)
            if len(self.purchased_shares) != 0:
                # Price entire portfolio's day high and low
                portfolio_high = self.cash_amount[date]
                portfolio_low = self.cash_amount[date]

                for ticker, share_count in self.purchased_shares.iteritems():
                    portfolio_high += share_count*self.data[ticker].loc[date, 'High']
                    portfolio_low += share_count*self.data[ticker].loc[date, 'Low']

                if portfolio_high > self.portfolio_global_high:
                    self.portfolio_global_high = portfolio_high
                    self.portfolio_local_low = self.portfolio_global_high
                elif portfolio_low < self.portfolio_local_low:
                    self.portfolio_local_low = portfolio_low

                    # Record max drawdown
                    #if ((self.portfolio_local_low / self.portfolio_global_high) - 1) < self.max_drawdown:
                    #    self.max_drawdown = (self.portfolio_local_low / self.portfolio_global_high) - 1

        # Close all open positions after finishing the backtest
        if len(self.purchased_shares) != 0:
            temp_purchased_shares = self.purchased_shares.copy()

            for ticker, share_count in temp_purchased_shares.iteritems():
                #current_invested_amount = self.mark_portfolio_to_market()
                # Mark the portfolio to market
                #current_invested_amount = 0.0
                #for k, v in self.purchased_shares.iteritems():
                #    current_invested_amount += v*self.data[k].loc[date, 'Open']

                # Determine at which share price to sell
                # TODO: Introduce slippage here
                #share_price = self.determine_share_price(is_bid=True, is_open_price=True)
                #share_price = (1 - self.ticker_spreads[key]/2) * self.data[key].loc[date, 'Open']

                # Record commission
                #commissions[date] += self.commission

                # Sell shares for cash
                #cash_amount[date] = self.prev_cash_amount + self.purchased_shares[key]*share_price - self.commission

                # End of day invested amount
                #invested_amount[date] = current_invested_amount - self.purchased_shares[key]*share_price

                # Record transaction
                #transactions[date][key] = {
                #    'position': 0,
                #    'share_count': self.purchased_shares[key],
                #    'share_price': share_price
                #}

                # Remove purchased record
                #del self.purchased_shares[key]

                self.execute_transaction(date=date, ticker=ticker, is_bid=True, share_count=None, position_percent=1.0)

        # Create data frame out of daily trade stats
        results = pd.DataFrame(portfolio_value.values(), columns=['Portfolio Value'], index=portfolio_value.keys())
        results['Cash'] = pd.Series(cash_amount.values(), index=cash_amount.keys())
        results['Invested'] = pd.Series(invested_amount.values(), index=invested_amount.keys())
        results['PnL'] = pd.Series(p_n_l.values(), index=p_n_l.keys())
        # results['Return'] = pd.Series(returns.values(), index=returns.keys())
        results['Commission'] = pd.Series(commissions.values(), index=commissions.keys())
        results['Transactions'] = pd.Series(transactions.values(), index=transactions.keys())
        results = results.sort_index()

        # # Compute period statistics
        # annual_avg_return = daily_results['Return'].mean() * 252
        # annual_std_dev = daily_results['Return'].std() * np.sqrt(252)
        # annual_semi_std_dev = daily_results['Return'].where(daily_results['Return'] < 0.0).std() * np.sqrt(252)
        # years_traded = (((self.dates[-1] - self.dates[0]).days + 1) / 365.0)
        # total_return = daily_results['Portfolio Value'][-1] / daily_results['Portfolio Value'][0]
        # cagr = total_return ** (1 / years_traded) - 1
        # sortino_ratio = float('NaN') if annual_semi_std_dev == 0 else annual_avg_return / annual_semi_std_dev
        # mar_ratio = float('NaN') if self.max_drawdown == 0 else -cagr / self.max_drawdown

        # # Create dictionary out of period stats
        # period_results = {
        #     'Max Drawdown': -self.max_drawdown,
        #     'Sharpe Ratio': annual_avg_return / annual_std_dev,
        #     'Sortino Ratio': sortino_ratio,
        #     'MAR Ratio': mar_ratio,
        #     # 'Information Ratio': 0.0,
        #     'CAGR': cagr,
        #     'Total Return': total_return - 1,
        #     'Annual Return': annual_avg_return,
        #     'Annual Volatility': annual_std_dev,
        #     'Start Portfolio Value': daily_results['Portfolio Value'][0],
        #     'End Portfolio Value': daily_results['Portfolio Value'][-1],
        #     'Total Trades': daily_results['Transactions'].where(daily_results['Transactions'] != {}).count() / 2,
        #     'Winning Trades': winning_trade_cnt,
        #     'Losing Trades': losing_trade_cnt,
        #     'Average Winning Trade': float('NaN') if len(winning_trade_returns) == 0 else np.mean(winning_trade_returns),
        #     'Average Losing Trade': float('NaN') if len(losing_trade_returns) == 0 else np.mean(losing_trade_returns),
        # }

        return results

    def execute_transaction(self, date, ticker, is_bid, share_count=None, position_percent=None):
        current_invested_amount = self.mark_portfolio_to_market()
        self.commissions[date] += self.commission

        # TODO: Determine how many shares to transact
        if share_count is not None:
            pass
        elif position_count is not None:
            pass
        else: # Error
            pass

        # TODO: Keep track of potential leverage!

        if is_bid: # Close position
            # TODO: Allow user to sell portions of position, currently closes entire position
            share_price = (1 - self.ticker_spreads[ticker] / 2) * self.data[ticker].loc[date, 'Open']
            self.cash_amount[date] = self.prev_cash_amount + self.purchased_shares[ticker] * share_price - self.commission
            self.invested_amount[date] = current_invested_amount - self.purchased_shares[ticker] * share_price
            self.transactions[date][ticker] = {
                'position': 0,
                'share_count': self.purchased_shares[ticker],
                'share_price': share_price
            }
            del self.purchased_shares[ticker]
        else:   # Open position
            share_price = (1 + self.ticker_spreads[ticker] / 2) * self.data[ticker].loc[date, 'Open']
            self.open_share_price[ticker] = share_price
            self.purchased_shares[key] = share_count #m.floor(self.prev_portfolio_value / share_price * value['portfolio_perc'])
            self.cash_amount[date] = self.prev_cash_amount - self.purchased_shares[ticker] * share_price - self.commission
            self.invested_amount[date] = self.prev_invested_amount + self.purchased_shares[ticker] * self.data[ticker].loc[date, 'Close']
            self.transactions[date][ticker] = {
                'position': 1,
                'share_count': self.purchased_shares[ticker],
                'share_price': share_price
            }

    def mark_portfolio_to_market(self):    
        if len(self.purchased_shares) != 0:
            temp_purchased_shares = self.purchased_shares.copy()

            # Determine current invested amount
            for key, value in temp_purchased_shares.iteritems():
                invested_amount += value*self.data[key].loc[date, 'Close']

            return invested_amount
