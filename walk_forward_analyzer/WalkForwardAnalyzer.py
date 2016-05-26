import numpy as np
import exceptions as ex
import pandas as pd
from pandas.tseries.offsets import BDay
from pprint import pprint


class WalkForwardAnalyzer(object):

    def __init__(self, in_sample_periods, out_of_sample_periods, sample_period, optimizer, backtester):
        self.in_sample_periods = in_sample_periods
        self.out_of_sample_periods = out_of_sample_periods
        self.sample_period = sample_period
        self.optimizer = optimizer
        self.backtester = backtester

    def run(self, data, start_date, end_date):
        sample_periods = self.create_sample_periods(data, start_date, end_date, self.in_sample_periods, \
            self.out_of_sample_periods, self.sample_period)
        pprint(sample_periods)
        exit(0)

    def create_sample_periods(self, data, start_date, end_date, in_sample_periods, out_of_sample_periods, sample_period):
        downsampled_dates = self._downsample_dates(data, start_date, end_date, in_sample_periods, sample_period)

        # Determine full in-sample and out-of-sample periods
        i = 0
        sample_periods = []
        while(True):
            # Setup in-sample and out-of-sample start and end dates
            sample_offset = i * out_of_sample_periods
            in_sample_start_date = downsampled_dates[sample_offset]
            in_sample_end_date = downsampled_dates[sample_offset + in_sample_periods - 1]
            out_of_sample_start_date = downsampled_dates[sample_offset + in_sample_periods]
            out_of_sample_end_date = downsampled_dates[sample_offset + in_sample_periods + out_of_sample_periods - 1]

            sample_periods.append(
                {
                    'in':   [in_sample_start_date, in_sample_end_date],
                    'out':  [out_of_sample_start_date, out_of_sample_end_date]
                }
            )

            # Exit the while loop before exceeding number of downsampled dates
            i = i + 1
            if(((i * out_of_sample_periods) + in_sample_periods + out_of_sample_periods - 1) >= len(downsampled_dates)):
                break

        # Make sure to add a sample period if there are overhanging end dates not accounted for
        if(out_of_sample_end_date <= end_date.date()):
            sample_offset = (i - 1) * out_of_sample_periods
            in_sample_start_date = downsampled_dates[sample_offset + out_of_sample_periods]
            in_sample_end_date = downsampled_dates[sample_offset + in_sample_periods + out_of_sample_periods - 1]
            out_of_sample_start_date = downsampled_dates[sample_offset + in_sample_periods + out_of_sample_periods]
            out_of_sample_end_date = downsampled_dates[-1]

            sample_periods.append(
                {
                    'in':   [in_sample_start_date, in_sample_end_date],
                    'out':  [out_of_sample_start_date, out_of_sample_end_date]
                }
            )

        return sample_periods

    def _downsample_dates(self, data, start_date, end_date, in_sample_periods, sample_period):
        downsampled_dates_per_frame = {}
        downsample_rule = self.sample_period_to_downsample_rule(sample_period)

        # Downsample all data sets and extract the dates
        downsampled_date_count = 0
        for name, frame in data.iteritems():
            downsampled_data = frame.resample(downsample_rule, label='right', convention='end').ffill()[:end_date]
            downsampled_dates_per_frame[name] = downsampled_data.axes[0].date

            # Make sure observation counts between different frames match
            if(downsampled_date_count != 0):
                if(downsampled_date_count != downsampled_dates_per_frame[name].size):
                    ex.AttributeError.message('ERROR: The number of observations after downsampling between frames must match.')
            else:
                downsampled_date_count = downsampled_dates_per_frame[name].size

        # Find the max oldest date from each of the data set's periods
        downsampled_dates = []
        for i in range(downsampled_date_count):
            all_dates = []
            for name, dates in downsampled_dates_per_frame.iteritems():
                all_dates.append(dates[i])

            downsampled_dates.append(np.max(all_dates))

        # Find the downsampled date which corresponds to the original start date
        start_date = pd.datetime.date(start_date)
        for i in range(downsampled_date_count):
            if(downsampled_dates[i] >= start_date):
                break

        return downsampled_dates[i-in_sample_periods:]

    def sample_period_to_downsample_rule(self, sample_period):
        sample_period = sample_period.lower()

        if(sample_period == "daily"):
            return "1D"
        elif(sample_period == "weekly"):
            return "1W"
        elif(sample_period == "monthly"):
            return "1M"
        elif(sample_period == "quarterly"):
            return "1Q"
        elif(sample_period == "yearly"):
            return "1Y"
