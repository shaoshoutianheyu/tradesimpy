import os
import pandas as pd
from DataSource import DataSource
from pandas.tseries.offsets import BDay


class CSVDataSource(DataSource):
	def __init__(self, csv_data_uri):
		super(CSVDataSource, self).__init__('CSV')

		self.csv_data_uri = csv_data_uri

	def request(self, tickers, ticker_types, start_date, end_date, history_window):
		# REQUIRED DATA MEMBER
		data_start_date = start_date - BDay(history_window + 21)

		# TODO: Check cache before executing request

		# Discover all existing CSVs with ticker names
		data = {}
		for ticker in tickers:
			for root, dirs, files in os.walk(self.csv_data_uri):
				ticker_file_name = ticker + '.csv'
				if ticker_file_name in files:
					data[ticker] = {}

					# Read all csv data into frame
					frame = pd.read_csv(os.path.join(root, ticker_file_name), index_col=0, parse_dates=True)
					
					# Trim the data based on the prescribed date range
					data[ticker] = self.trim_frame_observations(frame, ticker, start_date, end_date, history_window)

		return data
