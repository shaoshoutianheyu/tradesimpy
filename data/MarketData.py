import re
import pandas as pd
import Quandl
from pandas.tseries.offsets import BDay
from pprint import pprint
import exceptions as ex

QUANDL_API_KEY = 'B8h6uA58skuqwcAtL_tf'


def load_market_data(tickers, ticker_types, data_sources, start_date, end_date, history_window):
    print('Loading data...')
    raw_data = _request(tickers, ticker_types, data_sources, start_date, end_date, history_window)
    print('Data loaded!')
    print

    # Prepare data dictionary
    data_dict = {}
    for ticker in tickers:
        data_dict[ticker] = {}

    # Discover data needed for analysis process, especially for history windows
    for column_name, series in raw_data.iteritems():
        start = start_date

        # Start on valid date
        while start not in series.index:
            start += BDay(1)

        # Determine the data source for the given column series
        column_name_ticker_matches = [bool(re.search(ticker, column_name)) for ticker in tickers]
        if(len(column_name_ticker_matches) > 1):
            ex.AttributeError.message('ERROR: There is more than one of the same ticker name.')
        data_source_idx = column_name_ticker_matches.index(True)

        # Grab only the required data specified by the history window
        ticker, series_name = _column_name_to_ticker_series_name(column_name, data_sources[data_source_idx])
        start_period = raw_data[column_name][:start].sort_index(ascending=False)
        hist_start_date = start_period.index[history_window].to_datetime()
        data_dict[ticker][series_name] = raw_data[column_name][hist_start_date:]

    # Save data
    data = {}
    for ticker in tickers:
        data[ticker] = pd.DataFrame(data_dict[ticker])

    return data

def _request(tickers, ticker_types, data_sources, start_date, end_date, history_window):    
    data_start_date = start_date - BDay(history_window + 5)

    # Determine if we need to request data from multiple data sources
    data_source_lookup = {}
    unique_data_sources = list(set(data_sources))
    if len(unique_data_sources) > 1:
        # Map data sources to specific tickers and ticker types
        pass
    else:
        data_source_lookup = {unique_data_sources[0]: [tickers, ticker_types]}

    # Load market data per unique data source
    frames = []
    for data_source, ticker_info in data_source_lookup.iteritems():
        if(data_source == 'Quandl'):
            data_request = [ticker_types[i] + "/" + tickers[i] for i in range(len(tickers))]
            frames.append(Quandl.get(data_request, trim_start=data_start_date, trim_end=end_date, authtoken=QUANDL_API_KEY))
        elif(data_source == 'CSV'):
            pass
        else:
            ex.AttributeError.message('ERROR: Unknown data source %s for data request.' % (data_source))

    return pd.concat(frames)

def _column_name_to_ticker_series_name(column_name, data_source):
    if(data_source == 'Quandl' or data_source == 'CSV'):
        series_name = re.sub("^[\s\w.]+-\s+", "", column_name)
        ticker = re.sub("\s-[\s\w]+$", "", column_name)
        ticker = re.sub("^\w+.", "", ticker)
    else:
        ex.AttributeError.message('ERROR: Unknown data source %s for column name to ticker series name extraction.' % (data_source))

    return ticker, series_name
