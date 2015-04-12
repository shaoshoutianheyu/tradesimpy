from simulator_import import *
import math as m
import numpy as np
import pandas as pd


class Simulator(object):
    def __init__(self, capital_base, carry_over_trades=False, trading_algo=None, data=None):
        self.trading_algo = trading_algo
        self.data = data
        self.capital_base = capital_base
        self.start_dates = dict()
        self.portfolio_global_high = capital_base
        self.portfolio_local_low = capital_base
        self.max_drawdown = 0.0
        self.carry_over_trades = carry_over_trades

        self.purchased_shares = dict()
        self.prev_portfolio_value = self.capital_base
        self.prev_cash_amount = self.capital_base
        self.prev_invested_amount = 0.0

        if trading_algo is not None and data is not None:
            # Determine trading start dates for each ticker
            for ticker in self.trading_algo.tickers:
                self.start_dates[ticker] = data[ticker].iloc[self.trading_algo.hist_window_length].name

            # TODO: Make this more flexible for multiple tickers!
            self.dates =\
                data[self.trading_algo.tickers[0]][self.start_dates[self.trading_algo.tickers[0]]:].index.tolist()

    def run(self, capital_base=10000, trading_algo=None, data=None):
        self.capital_base = capital_base

        # Create trading algorithm if necessary
        if trading_algo is not None:
            self.trading_algo = trading_algo

        # Load data if necessary
        if data is not None:
            self.data = data

            # Determine trading start dates for each ticker
            for ticker in self.trading_algo.tickers:
                self.start_dates[ticker] = data[ticker].iloc[self.trading_algo.hist_window_length].name

            # TODO: Make this more flexible for multiple tickers!
            self.dates =\
                data[self.trading_algo.tickers[0]][self.start_dates[self.trading_algo.tickers[0]]:].index.tolist()

        # Intialize daily results structures
        portfolio_value = dict()
        p_n_l = dict()
        returns = dict()
        transactions = dict()
        invested_amount = dict()
        cash_amount = dict()
        commissions = dict()

        # Initialize simulation results helper variables
        algo_window_length = self.trading_algo.hist_window_length
        algo_data = dict()

        # Reset previous values if no trades should be carried over
        if not self.carry_over_trades:
            self.purchased_shares = dict()
            self.prev_portfolio_value = self.capital_base
            self.prev_cash_amount = self.capital_base
            self.prev_invested_amount = 0.0

        # Iterate over all trading days
        for date in self.dates:
            cash_amount[date] = 0.0
            invested_amount[date] = 0.0
            commissions[date] = 0.0
            transactions[date] = dict()

            for ticker in self.trading_algo.tickers:
                algo_data[ticker] = self.data[ticker][:date][-algo_window_length-1:-1]

            # Determine the trade decision for entire portfolio
            trade_desc = self.trading_algo.determine_trade_decision(algo_data)

            # Trade off of all trade decisions
            if len(trade_desc) != 0:
                for key, value in trade_desc.iteritems():
                    if value['position'] == 0:  # Close position
                        # Mark the portfolio to market
                        current_invested_amount = 0.0
                        for k, v in self.purchased_shares.iteritems():
                            current_invested_amount += v*self.data[k].loc[date, 'Open']

                        # Determine how many shares to purchase
                        # TODO: Introduce slippage here, set from config file
                        share_price = self.data[key].loc[date, 'Open']

                        # Record commission
                        # TODO: Set commission per trade from config file
                        commission = 1.0
                        commissions[date] += commission

                        # Sell shares for cash
                        cash_amount[date] = self.prev_cash_amount + self.purchased_shares[key]*share_price - commission

                        # End of day invested amount
                        invested_amount[date] = current_invested_amount - self.purchased_shares[key]*share_price

                        # Record transaction
                        transactions[date][key] = {
                            'position': 0,
                            'share_count': self.purchased_shares[key],
                            'share_price': share_price
                        }

                        # Remove purchased record
                        del self.purchased_shares[key]

                    elif value['position'] == 1:  # Open long position
                        # Determine how many shares to purchase
                        # TODO: Introduce slippage here, set from config file
                        share_price = self.data[key].loc[date, 'Open']
                        self.purchased_shares[key] =\
                            m.floor(self.prev_portfolio_value/share_price*value['portfolio_perc'])

                        # Record commission
                        # TODO: Set commission per trade from config file
                        commission = 1.0
                        commissions[date] += commission

                        # Purchase shares using cash
                        cash_amount[date] = self.prev_cash_amount - self.purchased_shares[key]*share_price - commission

                        # End of day invested amount
                        invested_amount[date] =\
                            self.prev_invested_amount + self.purchased_shares[key]*self.data[key].loc[date, 'Close']

                        # Record transaction
                        transactions[date][key] = {
                            'position': 1,
                            'share_count': self.purchased_shares[key],
                            'share_price': share_price
                        }
                    # TODO: Allow for short selling
                    elif value['position'] == -1:  # Open short position
                        pass
                        # # Determine how many shares to purchase
                        # # TODO: Introduce slippage here, set from config file
                        # share_price = self.data[key].loc[date, 'Open']
                        # purchased_shares[key] = -m.floor(prev_portfolio_value/share_price*value['portfolio_perc'])
                        #
                        # # Record commission
                        # # TODO: Set commission per trade from config file
                        # commission = 1.0
                        # commissions[date] += commission
                        #
                        # # Purchase shares using cash
                        # cash_amount[date] = prev_cash_amount - purchased_shares[key]*share_price - commission
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
            else:  # No trades, mark portfolio to market
                cash_amount[date] = self.prev_cash_amount

                # Determine current invested amount
                if len(self.purchased_shares) != 0:
                    for key, value in self.purchased_shares.iteritems():
                        invested_amount[date] += value*self.data[key].loc[date, 'Close']

            # Record more trade stats
            portfolio_value[date] = cash_amount[date] + invested_amount[date]
            p_n_l[date] = portfolio_value[date] - self.prev_portfolio_value
            returns[date] = (portfolio_value[date] / self.prev_portfolio_value) - 1.0

            # Remember current asset amounts for next iteration
            self.prev_cash_amount = cash_amount[date]
            self.prev_invested_amount = invested_amount[date]
            self.prev_portfolio_value = portfolio_value[date]

            # Monitor portfolio drawdown (conservatively)
            if len(self.purchased_shares) != 0:
                # Price entire portfolio's day high and low
                portfolio_high = cash_amount[date]
                portfolio_low = cash_amount[date]
                for key, value in self.purchased_shares.iteritems():
                    portfolio_high += value*self.data[key].loc[date, 'High']
                    portfolio_low += value*self.data[key].loc[date, 'Low']

                if portfolio_high > self.portfolio_global_high:
                    self.portfolio_global_high = portfolio_high
                    self.portfolio_local_low = self.portfolio_global_high
                elif portfolio_low < self.portfolio_local_low:
                    self.portfolio_local_low = portfolio_low

                    # Record max drawdown
                    if ((self.portfolio_local_low / self.portfolio_global_high) - 1) < self.max_drawdown:
                        self.max_drawdown = (self.portfolio_local_low / self.portfolio_global_high) - 1

        # Determine if all open positions should be closed
        if not self.carry_over_trades:
            # Close all open positions that exist
            if len(self.purchased_shares) != 0:
                temp_purchased_shares = self.purchased_shares.copy()
                for key, value in temp_purchased_shares.iteritems():
                    # Mark the portfolio to market
                    current_invested_amount = 0.0
                    for k, v in self.purchased_shares.iteritems():
                        current_invested_amount += v*self.data[k].loc[date, 'Open']

                    # Determine how many shares to purchase
                    # TODO: Introduce slippage here, set from config file
                    share_price = self.data[key].loc[date, 'Open']

                    # Record commission
                    # TODO: Set commission per trade from config file
                    commission = 1.0
                    commissions[date] += commission

                    # Sell shares for cash
                    cash_amount[date] = self.prev_cash_amount + self.purchased_shares[key]*share_price - commission

                    # End of day invested amount
                    invested_amount[date] = current_invested_amount - self.purchased_shares[key]*share_price

                    # Record transaction
                    transactions[date][key] = {
                        'position': 0,
                        'share_count': self.purchased_shares[key],
                        'share_price': share_price
                    }

                    # Remove purchased record
                    del self.purchased_shares[key]

        # Create data frame out of daily trade stats
        daily_results = pd.DataFrame(portfolio_value.values(), columns=['Portfolio Value'], index=portfolio_value.keys())
        daily_results['Cash'] = pd.Series(cash_amount.values(), index=cash_amount.keys())
        daily_results['Invested'] = pd.Series(invested_amount.values(), index=invested_amount.keys())
        daily_results['PnL'] = pd.Series(p_n_l.values(), index=p_n_l.keys())
        daily_results['Return'] = pd.Series(returns.values(), index=returns.keys())
        daily_results['Commission'] = pd.Series(commissions.values(), index=commissions.keys())
        daily_results['Transactions'] = pd.Series(transactions.values(), index=transactions.keys())
        daily_results = daily_results.sort_index()

        # Compute period statistics
        annual_avg_return = daily_results['Return'].mean() * 252
        annual_std_dev = daily_results['Return'].std() * np.sqrt(252)
        annual_semi_std_dev = daily_results['Return'].where(daily_results['Return'] < 0.0).std() * np.sqrt(252)
        years_traded = (((self.dates[-1] - self.dates[0]).days + 1) / 365.0)
        total_return = daily_results['Portfolio Value'][-1] / daily_results['Portfolio Value'][0]
        cagr = total_return ** (1 / years_traded) - 1
        sortino_ratio = float('NaN') if annual_semi_std_dev == 0 else annual_avg_return / annual_semi_std_dev
        mar_ratio = float('NaN') if self.max_drawdown == 0 else -cagr / self.max_drawdown

        # Create dictionary out of period stats
        period_results = {
            'Max Drawdown': -self.max_drawdown,
            'Sharpe Ratio': annual_avg_return / annual_std_dev,
            'Sortino Ratio': sortino_ratio,
            'MAR Ratio': mar_ratio,
            # 'Information Ratio': 0.0,
            'CAGR': cagr,
            'Total Return': total_return - 1,
            'Annual Return': annual_avg_return,
            'Annual Volatility': annual_std_dev,
            'Total Trades': daily_results['Transactions'].where(daily_results['Transactions'] != {}).count(),
            'Start Portfolio Value': daily_results['Portfolio Value'][0],
            'End Portfolio Value': daily_results['Portfolio Value'][-1]
        }

        return period_results, daily_results
