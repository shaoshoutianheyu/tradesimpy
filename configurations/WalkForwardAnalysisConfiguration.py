from Configuration import Configuration
import json


class WalkForwardAnalysisConfiguration(Configuration):
    def __init__(self, config_uri):
        super(WalkForwardAnalysisConfiguration, self).__init__(config_uri)

        # Read config data
        with open(config_uri, mode='r') as f:
            config_data = json.loads(f.read())

        # Define data members
        self.cash = float(config_data['cash'])
        self.num_processors = int(config_data['num_processors'])
        self.optimizer_name = config_data['optimizer_name']
        self.optimization_metric = config_data['optimization_metric']
        self.optimization_metric_ascending = bool(config_data['optimization_metric_ascending'])
        self.optimization_parameters = config_data['optimization_parameters']
        self.in_sample_periods = int(config_data['in_sample_periods'])
        self.out_of_sample_periods = int(config_data['out_of_sample_periods'])
        self.sample_period = config_data['sample_period']

        # Validate input parameters
        if(not self.cash):
            raise ValueError("Input cash in Configuration is invalid.")
        if(not self.num_processors):
            raise ValueError("Input num_processors in WalkForwardAnalysisConfiguration is invalid.")
        if(not self.optimizer_name):
            raise ValueError("Input optimizer_name in WalkForwardAnalysisConfiguration is invalid.")
        if(not self.optimization_metric):
            raise ValueError("Input optimization_metric in WalkForwardAnalysisConfiguration is invalid.")
        if(not self.optimization_metric_ascending):
            raise ValueError("Input optimization_metric_ascending in WalkForwardAnalysisConfiguration is invalid.")
        if(not self.optimization_parameters):
            raise ValueError("Input optimization_parameters in WalkForwardAnalysisConfiguration is invalid.")
        if(not self.in_sample_periods):
            raise ValueError("Input in_sample_periods in WalkForwardAnalysisConfiguration is invalid.")
        if(not self.out_of_sample_periods):
            raise ValueError("Input out_of_sample_periods in WalkForwardAnalysisConfiguration is invalid.")
        if(not self.sample_period):
            raise ValueError("Input sample_period in WalkForwardAnalysisConfiguration is invalid.")

    def __str__(self):
        super(WalkForwardAnalysisConfiguration, self).__str__()

        print('Cash:                             %s' % (self.cash))
        print('Number of processors:             %s' % (self.num_processors))
        print('Optimizer name:                   %s' % (self.optimizer_name))
        print('Optimization metric:              %s' % (self.optimization_metric))
        print('Optimization metric ascending:    %s' % (self.optimization_metric_ascending))
        print('Optimization parameters:')
        for name, value in self.optimization_parameters.iteritems():
            print('                                  %s : %s' % (name, value))
        print('In-sample periods:                %s' % (self.in_sample_periods))
        print('Out-of-sample periods:            %s' % (self.out_of_sample_periods))
        print('Sample period:                    %s' % (self.sample_period))
        print('***************************************************************************')
        print
