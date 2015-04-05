import pandas.io.data as web


# TODO: Make this work for multiple securities
# def load_data(ticker='SPY', start='1900', adjust_close=False):
def load_data(tickers, start, end, adjusted=False):
    data = web.DataReader(tickers, data_source='yahoo', start=start, end=end)
    # print data
    # print data.minor_xs('SPY')

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

    return data