from Configuration import Configuration
import json


class OptimizationConfiguration(Configuration):
    def __init__(self, config_uri):
        super(OptimizationConfiguration, self).__init__(config_uri)

        # Read config data
        with open(config_uri, mode='r') as f:
            config_data = json.loads(f.read())

        # Define data members
        self.num_processors = int(config_data['num_processors'])
        self.optimizer_name = config_data['optimizer_name']
        self.optimization_metric = config_data['optimization_metric']
        self.optimization_metric_ascending = bool(config_data['optimization_metric_ascending'])
        self.optimization_parameters = config_data['optimization_parameters']

        # Validate input parameters
        if(not self.num_processors):
            raise ValueError("Input num_processors in OptimizationConfiguration is invalid.")
        if(not self.optimizer_name):
            raise ValueError("Input optimizer_name in OptimizationConfiguration is invalid.")
        if(not self.optimization_metric):
            raise ValueError("Input optimization_metric in OptimizationConfiguration is invalid.")
        if(not self.optimization_metric_ascending):
            raise ValueError("Input optimization_metric_ascending in OptimizationConfiguration is invalid.")
        if(not self.optimization_parameters):
            raise ValueError("Input optimization_parameters in OptimizationConfiguration is invalid.")

    def __str__(self):
        super(OptimizationConfiguration, self).__str__()

        print('Number of processors:             %s' % (self.num_processors))
        print('Optimizer name:                   %s' % (self.optimizer_name))
        print('Optimization metric:              %s' % (self.optimization_metric))
        print('Optimization metric ascending:    %s' % (self.optimization_metric_ascending))
        print('Optimization parameters:')
        for name, value in self.optimization_parameters.iteritems():
            print('                                  %s : %s' % (name, value))
        print('**************************************************************************')
        print
