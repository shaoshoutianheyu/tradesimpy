from Configuration import Configuration
import json


class BacktestConfiguration(Configuration):
    def __init__(self, config_uri):
        super(BacktestConfiguration, self).__init__(config_uri)

        # Read config data
        with open(config_uri, mode='r') as f:
            config_data = json.loads(f.read())

        # Define data members
        self.cash = float(config_data['cash'])
        self.algorithm_parameters = config_data['algorithm_parameters']

        # Validate input parameters
        if(not self.cash):
            raise ValueError("Input cash in Configuration is invalid.")
        if(not self.algorithm_parameters):
            raise ValueError("Input algorithm_parameters in BacktestConfiguration is invalid.")

    def __str__(self):
        super(BacktestConfiguration, self).__str__()

        print('Cash:                             %s' % (self.cash))
        print('Algorithm parameters:')
        for name, value in self.algorithm_parameters.iteritems():
            print('                                  %s : %s' % (name, value))
        print('***************************************************************************')
        print
