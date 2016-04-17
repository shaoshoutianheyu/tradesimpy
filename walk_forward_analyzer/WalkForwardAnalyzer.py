import numpy as np
import exceptions as ex
from pandas.tseries.offsets import BDay
from pprint import pprint


class WalkForwardAnalyzer(object):

    def __init__(self, in_sample_periods, out_of_sample_periods, sample_period, optimizer, backtester):
        self.in_sample_periods = in_sample_periods
        self.out_of_sample_periods = out_of_sample_periods
        self.sample_period = sample_period
        self.optimizer = optimizer
        self.backtester = backtester

    def run(self, start_date, end_date, data):
        sample_periods = self.create_sample_periods(start_date, end_date, data, self.in_sample_periods, \
            self.out_of_sample_periods, self.sample_period)
        pprint(sample_periods)
        exit(0)

    def create_sample_periods(self, start_date, end_date, data, in_sample_periods, out_of_sample_periods, sample_period):
        sample_periods = []

        downsampled_dates = self.downsample_dates(start_date, end_date, data, sample_period)
        pprint(downsampled_dates)
        exit(0)

        # Determine and store all sample periods
        while(start_date + BDay(out_sample_day_cnt - 1)) <= end_date:
            inStart = start_date - BDay(in_sample_day_cnt)
            inEnd = start_date - BDay(1)
            outStart = start_date
            outEnd = start_date + BDay(out_sample_day_cnt - 1)

            sample_periods.append(
                {
                    'in':   [inStart, inEnd],
                    'out':  [outStart, outEnd]
                }
            )

            # Update new start date
            start_date = start_date + BDay(out_sample_day_cnt)

    def downsample_dates(self, start_date, end_date, data, sample_period):
        downsampled_dates_per_frame = {}
        downsample_rule = self.sample_period_to_downsample_rule(sample_period)

        # Downsample all data sets and extract the dates
        downsampled_date_count = 0
        for name, frame in data.iteritems():
            downsampled_data = frame.resample(downsample_rule, label='right', convention='end')[start_date:end_date]
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

        return downsampled_dates

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
