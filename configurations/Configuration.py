
class Configuration(object):
    def __init__(self, algorithm_name, start_date, end_date, cash, time_resolution, tickers, ticker_types,
                 ticker_series_names, data_sources, commission):

        # Define data members
        self.algorithm_name = algorithm_name
        self.start_date = start_date
        self.end_date = end_date
        self.cash = cash
        self.time_resolution = time_resolution
        self.tickers = tickers
        self.ticker_types = ticker_types
        self.ticker_series_names = ticker_series_names
        self.data_sources = data_sources
        self.commission = commission

        self.validate_input_parameters()

    def validate_input_parameters(self):
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

    def __str__(self):
        print('***************** CONFIGURATION PARAMETERS *****************')
        print('Algorithm name:          %s' % (self.algorithm_name))
        print('Start date:              %s' % (self.start_date))
        print('End date:                %s' % (self.end_date))
        print('Cash:                    %s' % (self.cash))
        print('Time resolution:         %s' % (self.time_resolution))
        print('Tickers:')
        for ticker in self.tickers:
            print('                        %s' % (ticker))
        print('Ticker types:')
        for ticker_type in self.ticker_types:
            print('                        %s' % (ticker_type))
        print('Ticker series names:')
        for ticker_series_name in self.ticker_series_names:
            print('                        %s' % (ticker_series_name))
        print('Data sources:')
        for data_source in self.data_sources:
            print('                        %s' % (data_source))
        print('Commission:              %s' % (self.commission))
