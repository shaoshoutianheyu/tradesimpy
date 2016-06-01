import re
import pandas as pd
import quandl
from pandas.tseries.offsets import BDay
import data_source_factory as dsf

def load_market_data(tickers, ticker_types, data_sources, start_date, end_date, history_window):
    # Create the unique data sources
    unique_data_sources = dsf.create_data_sources(data_sources)

    # Group the tickers and ticker types by data source
    frame = pd.DataFrame({'tickers': tickers, 'ticker_types': ticker_types, 'data_sources': data_sources})
    grouped_frame = frame.groupby(['data_sources'])

    # Request and save data from each data source group
    data = {}
    for key, group in grouped_frame:
        data_source = unique_data_sources[key]
        group_data = data_source.request(group['tickers'], group['ticker_types'], start_date, end_date, history_window)

        # Check if there are equal tickers but with different data sources
        for key in group_data.keys():
            if(key in data.keys()):
                raise KeyError("There is more than one of the same ticker name: %s" % key)

        # Add data
        data.update(group_data)

    return data
