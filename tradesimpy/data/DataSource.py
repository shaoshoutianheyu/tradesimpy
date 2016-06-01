from pandas.tseries.offsets import BDay


class DataSource(object):
	def __init__(self, name, api_key=None):
		self.name = name
		self.api_key = api_key

	def trim_series_observations(self, series, start_date, history_window):
		start = start_date

		# Start on valid date
		while start not in series.index:
			start += BDay(1)

		# Grab only the required data specified by the history window
		start_period = series[:start].sort_index(ascending=False)
		hist_start_date = start_period.index[history_window].to_datetime()

		return series[hist_start_date:]
