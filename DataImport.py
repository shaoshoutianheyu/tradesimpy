import pandas.io.data as web
import numpy as np


def load_data(tickers, start, end, adjusted):
    data = web.DataReader(tickers, data_source='yahoo', start=start, end=end)

    if adjusted:
        adj = data['Adj Close'] - data['Close']
        data['Open'] += adj
        data['High'] += adj
        data['Low'] += adj
        data['Close'] += adj
        data = data.drop('Adj Close', axis=0)

    # Fill in all missing data
    data = data.bfill()

    # Create dictionary of data-frames
    result = dict()
    for ticker in tickers:
        result[ticker] = data.minor_xs(ticker)

    return result


def get_benchmark_comparison(benchmark_ticker, start_date, end_date, capital_base):
    stats = dict()

    # Pull benchmark data, scale, and get statistics for comparison analysis
    benchmark_data = load_data([benchmark_ticker], start_date, end_date, adjusted=True)[benchmark_ticker]
    stats['Portfolio Value'] = benchmark_data['Close'] * (capital_base / benchmark_data['Close'][0])
    benchmark_returns =\
        (stats['Portfolio Value'] - stats['Portfolio Value'].shift(1)) / stats['Portfolio Value'].shift(1)
    stats['Average Return'] = benchmark_returns.mean() * 252
    stats['Return Std Dev'] = benchmark_returns.std() * np.sqrt(252)
    benchmark_semi_std_dev = benchmark_returns.where(benchmark_returns < 0.0).std() * np.sqrt(252)
    stats['Sharpe Ratio'] =\
        float('NaN') if stats['Return Std Dev'] == 0 else stats['Average Return'] / stats['Return Std Dev']
    stats['Sortino Ratio'] =\
        float('NaN') if benchmark_semi_std_dev == 0 else  stats['Average Return'] / benchmark_semi_std_dev
    stats['CAGR'] =\
        (stats['Portfolio Value'][-1] / stats['Portfolio Value'][0]) ** (1 / ((end_date - start_date).days / 365.0)) - 1

    global_high = 0.0
    local_low = 0.0
    benchmark_max_drawdown = 0.0
    for p in benchmark_data.index:
        if benchmark_data.ix[p]['High'] > global_high:
            global_high = benchmark_data.ix[p]['High']
            local_low = global_high

        if benchmark_data.ix[p]['Low'] < local_low:
            local_low = benchmark_data.ix[p]['Low']

            # Record max drawdown
            if ((local_low / global_high) - 1) < benchmark_max_drawdown:
                benchmark_max_drawdown = (local_low / global_high) - 1
    stats['Max Drawdown'] = -benchmark_max_drawdown
    stats['MAR Ratio'] = float('NaN') if benchmark_max_drawdown == 0 else -stats['CAGR'] / benchmark_max_drawdown

    return stats
