from simulator_import import *
import math as m
import numpy as np
import pandas as pd


class Simulator(object):
    def __init__(self, trading_algo, data, capital_base):
        self.trading_algo = trading_algo
        self.data = data
        self.capital_base = capital_base
        self.start_dates = dict()

        # Determine trading start dates for each ticker
        for ticker in self.trading_algo.tickers:
            self.start_dates[ticker] = data[ticker].iloc[self.trading_algo.hist_window_length].name

        # TODO: Make this more flexible for multiple tickers!
        self.dates = data[self.trading_algo.tickers[0]][self.start_dates[self.trading_algo.tickers[0]]:].index.tolist()


    def run(self):
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
        purchased_shares = dict()
        prev_portfolio_value = self.capital_base
        prev_cash_amount = self.capital_base
        prev_invested_amount = 0.0
        max_drawdown = 0.0
        global_high = self.capital_base
        local_low = 0.0

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
                        for k, v in purchased_shares.iteritems():
                            current_invested_amount += v*self.data[key].loc[date, 'Open']

                        # Determine how many shares to purchase
                        # TODO: Introduce slippage here, set from config file
                        share_price = self.data[key].loc[date, 'Open']

                        # Record commission
                        # TODO: Set commission per trade from config file
                        commission = 1.0
                        commissions[date] += commission

                        # Sell shares for cash
                        cash_amount[date] = prev_cash_amount + purchased_shares[key]*share_price - commission

                        # End of day invested amount
                        invested_amount[date] = current_invested_amount - purchased_shares[key]*share_price

                        # Record transaction
                        transactions[date][key] = {
                            'position': 0,
                            'share_count': purchased_shares[key],
                            'share_price': share_price
                        }

                        # Remove purchased record
                        del purchased_shares[key]

                    elif value['position'] == 1:  # Open long position
                        # Determine how many shares to purchase
                        # TODO: Introduce slippage here, set from config file
                        share_price = self.data[key].loc[date, 'Open']
                        purchased_shares[key] = m.floor(prev_portfolio_value/share_price*value['portfolio_perc'])

                        # Record commission
                        # TODO: Set commission per trade from config file
                        commission = 1.0
                        commissions[date] += commission

                        # Purchase shares using cash
                        cash_amount[date] = prev_cash_amount - purchased_shares[key]*share_price - commission

                        # End of day invested amount
                        invested_amount[date] =\
                            prev_invested_amount + purchased_shares[key]*self.data[key].loc[date, 'Close']

                        # Record transaction
                        transactions[date][key] = {
                            'position': 1,
                            'share_count': purchased_shares[key],
                            'share_price': share_price
                        }
                    # TODO: Allow for short selling
                    elif trade_desc['position'] == -1:  # Open short position
                        pass
            else:  # No trades, mark portfolio to market
                cash_amount[date] = prev_cash_amount

                # Determine current invested amount
                if len(purchased_shares) != 0:
                    for key, value in purchased_shares.iteritems():
                        invested_amount[date] += value*self.data[key].loc[date, 'Close']

            # Record more trade stats
            portfolio_value[date] = cash_amount[date] + invested_amount[date]
            p_n_l[date] = portfolio_value[date] - prev_portfolio_value
            returns[date] = (portfolio_value[date] / prev_portfolio_value) - 1.0

            # Remember current asset amounts for next iteration
            prev_cash_amount = cash_amount[date]
            prev_invested_amount = invested_amount[date]
            prev_portfolio_value = portfolio_value[date]

            # Monitor portfolio drawdown
            if portfolio_value[date] > global_high:
                global_high = portfolio_value[date]
                local_low = global_high
            elif portfolio_value[date] < local_low:
                local_low = portfolio_value[date]

                # Record max drawdown
                if ((local_low / global_high) - 1) < max_drawdown:
                    max_drawdown = (local_low / global_high) - 1

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
        annual_semi_std_dev = daily_results['Return'].where(daily_results['Return'] >= 0.0).std() * np.sqrt(252)
        years_traded = ((self.dates[-1] - self.dates[0]).days / 365.0)

        # Create dictionary out of period stats
        period_results = {
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': annual_avg_return / annual_std_dev,
            'Sortino Ratio': annual_avg_return / annual_semi_std_dev,
            # 'Information Ratio': 0.0,
            'CAGR':
                (daily_results['Portfolio Value'][-1] / daily_results['Portfolio Value'][0]) ** (1 / years_traded) - 1,
            'Annual Return': annual_avg_return,
            'Annual Volatility': annual_std_dev,
            'Total Trades': daily_results['Transactions'].where(daily_results['Transactions'] != {}).count(),
        }

        return period_results, daily_results
