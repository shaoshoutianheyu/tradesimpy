import re
from DataSource import DataSource


class CSVDataSource(DataSource):
	def __init__(self):
		super(CSVDataSource, self).__init__('CSV')

	def request(tickers, ticker_types, start_date, end_date, history_window):
		raise NotImplementedError()

	def column_name_to_ticker_series_name(column_name):
		series_name = re.sub("^[\s\w/]+-\s+", "", column_name)
		ticker = re.sub("\s-[\s\w]+$", "", column_name)
		ticker = re.sub("^\w+.", "", ticker)

		return ticker, series_name
