import re
import quandl
import pandas as pd
from DataSource import DataSource
from pandas.tseries.offsets import BDay

QUANDL_API_KEY = 'B8h6uA58skuqwcAtL_tf'


class QuandlDataSource(DataSource):
	def __init__(self):
		super(QuandlDataSource, self).__init__('Quandl', QUANDL_API_KEY)

	def request(self, tickers, ticker_types, start_date, end_date, history_window):
		# REQUIRED DATA MEMBER
		data_start_date = start_date - BDay(history_window + 21)

		# TODO: Check cache before executing request
		
		# Build request and execute
		quandl.ApiConfig.api_key = self.api_key
		data_request = [ticker_types[i] + "/" + tickers[i] for i in range(len(tickers))]
		raw_data = quandl.get(data_request, trim_start=data_start_date, trim_end=end_date)

		# Prepare data dictionary
		data_dict = {}
		for ticker in tickers:
			data_dict[ticker] = {}

	    # Discover data needed for analysis process, especially for history windows
		for column_name, series in raw_data.iteritems():
			ticker_name, series_name = self.column_name_to_ticker_series_name(column_name)
			data_dict[ticker_name][series_name] = self.trim_series_observations(series, start_date, end_date, history_window)

		# Save data as dictionary of data frames
		data = {}
		for ticker in tickers:
			data[ticker] = pd.DataFrame(data_dict[ticker])

		return data
		
	def column_name_to_ticker_series_name(self, column_name):
		series_name = re.sub("^[\s\w/]+-\s+", "", column_name)
		ticker_name = re.sub("\s-[\s\w]+$", "", column_name)
		ticker_name = re.sub("^\w+.", "", ticker_name)

		return ticker_name, series_name
