import pandas as pd
import logging as log
from pandas.tseries.offsets import BDay


class DataSource(object):
	def __init__(self, name, api_key=None):
		self.name = name
		self.api_key = api_key

	def trim_series_observations(self, series, ticker, series_name, start_date, end_date, history_window):
		start = start_date

		# Start on valid date
		while start not in series.index:
			start += BDay(1)

		# Grab only the required data specified by the history window
		series = series.sort_index(ascending=True)
		start_period = series[:start].sort_index(ascending=False)
		hist_start_date = None
		try:
			hist_start_date = start_period.index[history_window].to_datetime()
		except Exception, e:
			if(type(e) == IndexError):
				raise IndexError("The history window %d for %s.%s is too long for the start date %s." \
					% (history_window, ticker, series_name, start_date))
			else:
				raise e
		else:
			log.info("Trimmed time series %s.%s: (%s - %s)" % (ticker, series_name, hist_start_date, end_date))

		return series[hist_start_date:end_date]

	def trim_frame_observations(self, frame, ticker, start_date, end_date, history_window):
		trimmed_data = {}

		# Trim all time series
		for column_name, series in frame.iteritems():
			trimmed_data[column_name] = self.trim_series_observations(series, ticker, column_name, \
				start_date, end_date, history_window)

		return pd.DataFrame(trimmed_data)
