import re
import pandas as pd
import quandl
import numpy as np
import logging as log
import data_source_factory as dsf
from pandas.tseries.offsets import BDay
from datetime import datetime

def load_market_data(tickers, ticker_types, data_sources, start_date, end_date, history_window, csv_data_uri=None):
    # Check for unique tickers
    if(len(tickers) != len(list(set(tickers)))):
        raise ValueError("There are non-unique tickers set for loading.")

    # Create the unique data sources
    unique_data_sources = dsf.create_data_sources(data_sources, csv_data_uri)

    # Group the tickers and ticker types by data source
    frame = pd.DataFrame({'tickers': tickers, 'ticker_types': ticker_types, 'data_sources': data_sources})
    grouped_frame = frame.groupby(['data_sources'])

    # Request and save data from each data source group
    data = {}
    for key, group in grouped_frame:
        data_source = unique_data_sources[key]
        group_data = data_source.request(group['tickers'], group['ticker_types'], start_date, end_date, history_window)

        # Check if data request failed for all tickers
        if(not group_data):
            raise ValueError("The data request failed for all tickers from data source %s" % key)

        # Check if data request failed for certain tickers
        for ticker in group['tickers']:
            if(group_data[ticker].empty):
                raise ValueError("The data request failed for ticker %s from data source %s" % (ticker, key))

        # Check for issues in data
        for ticker_name, series in group_data.iteritems():
            # Check for equal tickers but with different data sources
            if(ticker_name in data.keys()):
                raise ValueError("There is more than one of the same ticker name loaded: %s" % ticker_name)

            # Check for proper date ranges in data
            if(history_window > 0):
                if(series.index[history_window-1] > start_date):
                    log.warning("The data (with history window) for ticker %s has a start date greater than %s: %s" \
                        % (ticker_name, start_date, series.index[history_window-1]))
            else:
                if(series.index[0] > start_date):
                    log.warning("The data for ticker %s has a start date greater than %s: %s" \
                        % (ticker_name, start_date, series.index[0]))
            if(series.index[-1] < end_date):
                log.warning("The data for ticker %s has a end date less than %s: %s" \
                    % (ticker_name, end_date, series.index[-1]))

        data.update(group_data)

    return data
