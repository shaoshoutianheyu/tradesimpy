from Configuration import Configuration


class BacktestConfiguration(Configuration):
    def __init__(self, algorithm_name, start_date, end_date, cash, time_resolution, tickers, ticker_types,
                 ticker_series_names, data_sources, commission, algorithm_parameters):
        super(BacktestConfiguration, self).__init__(algorithm_name, start_date, end_date, cash, time_resolution,
                                                    tickers, ticker_types, ticker_series_names, data_sources,
                                                    commission)

        # Define data members
        self.algorithm_parameters = algorithm_parameters

        self.validate_input_parameters()

    def validate_input_parameters(self):
        if(not self.algorithm_parameters):
            raise ValueError("Input algorithm_parameters in BacktestConfiguration is invalid.")

    def __str__(self):
        print(super(BacktestConfiguration, self))
        print('Algorithm parameters:')
        for name, value in self.algorithm_parameters.iteritems():
            print('                        %s : %s' % (name, value))
        print('************************************************************')
        print
