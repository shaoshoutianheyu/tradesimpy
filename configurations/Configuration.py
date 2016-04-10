import json
import pandas as pd


class Configuration(object):
    def __init__(self, config_uri):

        # Read config data
        with open(config_uri, mode='r') as f:
            config_data = json.loads(f.read())

        # Define data members
        self.algorithm_name = config_data['algorithm_name']
        self.start_date = pd.datetime.strptime(config_data['start_date'], "%Y-%m-%d")
        self.end_date = pd.datetime.strptime(config_data['end_date'], "%Y-%m-%d")
        self.cash = float(config_data['cash'])
        self.time_resolution = config_data['time_resolution']
        self.tickers = config_data['tickers']
        self.ticker_types = config_data['ticker_types']
        self.ticker_series_names = config_data['ticker_series_names']
        self.data_sources = config_data['data_sources']
        self.ticker_spreads = config_data['ticker_spreads']
        self.commission = float(config_data['commission'])
        self.history_window = int(config_data['history_window'])

        # Validate input parameters
        if(not self.algorithm_name):
            raise ValueError("Input algorithm_name in Configuration is invalid.")
        if(not self.start_date):
            raise ValueError("Input start_date in Configuration is invalid.")
        if(not self.end_date):
            raise ValueError("Input end_date in Configuration is invalid.")
        if(not self.cash):
            raise ValueError("Input cash in Configuration is invalid.")
        if(not self.time_resolution):
            raise ValueError("Input time_resolution in Configuration is invalid.")
        if(not self.tickers):
            raise ValueError("Input tickers in Configuration is invalid.")
        if(not self.ticker_types):
            raise ValueError("Input ticker_types in Configuration is invalid.")
        if(not self.ticker_series_names):
            raise ValueError("Input ticker_series_names in Configuration is invalid.")
        if(not self.data_sources):
            raise ValueError("Input data_sources in Configuration is invalid.")
        if(len(self.tickers) != len(self.ticker_types) and len(self.ticker) != len(self.ticker_series_names) and len(self.tickers) != len(self.data_sources)):
            raise ValueError("Input tickers, ticker_types, ticker_series_names, and data_source in Configuration must be equal in count.")
        if(self.start_date > self.end_date):
            raise ValueError("Input start_date must be less than or equal to end_date.")

    def __str__(self):
        print('************************ CONFIGURATION PARAMETERS ************************')
        print('Algorithm name:                   %s' % (self.algorithm_name))
        print('Start date:                       %s' % (self.start_date))
        print('End date:                         %s' % (self.end_date))
        print('Cash:                             %s' % (self.cash))
        print('Time resolution:                  %s' % (self.time_resolution))
        print('Tickers:')
        for ticker in self.tickers:
            print('                                  %s' % (ticker))
        print('Ticker types:')
        for ticker_type in self.ticker_types:
            print('                                  %s' % (ticker_type))
        print('Ticker series names:')
        for ticker_series_name in self.ticker_series_names:
            print('                                  %s' % (ticker_series_name))
        print('Data sources:')
        for data_source in self.data_sources:
            print('                                  %s' % (data_source))
        print('Commission:                       %s' % (self.commission))
        print('History window:                   %s' % (self.history_window))
