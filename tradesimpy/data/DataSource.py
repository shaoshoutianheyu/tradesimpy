import pandas as pd
from pandas.tseries.offsets import BDay


class DataSource(object):
	def __init__(self, name, api_key=None):
		self.name = name
		self.api_key = api_key

	def trim_series_observations(self, series, start_date, end_date, history_window):
		start = start_date

		# Start on valid date
		while start not in series.index:
			start += BDay(1)

		# Grab only the required data specified by the history window
		series = series.sort_index(ascending=True)
		start_period = series[:start].sort_index(ascending=False)
		hist_start_date = start_period.index[history_window].to_datetime()

		return series[hist_start_date:end_date]

	def trim_frame_observations(self, frame, start_date, end_date, history_window):
		trimmed_data = {}

		# Trim all time series
		for column_name, series in frame.iteritems():
			trimmed_data[column_name] = self.trim_series_observations(series, start_date, end_date, history_window)

		return pd.DataFrame(trimmed_data)
