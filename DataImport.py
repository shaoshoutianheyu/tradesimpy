import pandas.io.data as web


def load_data(tickers, start, end, adjusted=False):
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
    # data = data.ffill()

    # Create dictionary of data-frames
    result = dict()
    for ticker in tickers:
        result[ticker] = data.minor_xs(ticker)

    return result