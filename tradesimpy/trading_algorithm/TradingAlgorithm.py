import sys
import re
import inspect


class TradingAlgorithm(object):

    def __init__(self, tickers, history_window, parameters):
        # Data members
        self.tickers = tickers
        self.history_window = history_window
        self.parameters = parameters

        # Initialize to no current open positions
        self.position_is_open = {}
        for ticker in self.tickers:
            self.position_is_open[ticker] = False

    def set_parameters(self, parameters):
    	self.parameters = parameters

    @staticmethod
    def create_trading_algorithm(algorithm_uri, tickers, history_window, algorithm_parameters = None):
        # Check if the path points to a python file
        if algorithm_uri[-3:] != '.py':
            raise NameError("The trading algorithm URI must include the Python file.")

        # Add path to system path
        dir_name = re.sub("/\w+\.py", "", algorithm_uri) + '/'
        sys.path.append(dir_name)

        # Import the module
        module_name = re.sub("^.*/", "", algorithm_uri)
        module_name = re.sub("\.py$", "", module_name)
        __import__(module_name, globals(), locals(), ['*'])
        
        # Get the class
        cls = getattr(sys.modules[module_name], module_name)
        
        # Check class
        if not inspect.isclass(cls):
           raise TypeError("%s is not a class" % module_name)
        
        return cls(tickers, history_window, algorithm_parameters)
