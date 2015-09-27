import pandas as pd


class SystemParameters(object):

    def __init__(self, configData):
        # Read in config parameters
        self.opt_name = configData['opt_method'].lower()
        self.opt_metric = configData['opt_metric']
        self.opt_metric_asc = bool(configData['opt_metric_asc'])
        self.algo_name = configData['algo_name'].lower()
        self.long_only = bool(configData['long_only'])
        self.capital_base = float(configData['capital_base'])
        self.commission = float(configData['commission'])
        self.benchmark_ticker = configData['benchmark_ticker']
        self.tickers_spreads = configData['tickers_spreads']
        self.start_date = pd.datetime.strptime(configData['start_date'], "%Y-%m-%d")
        self.end_date = pd.datetime.strptime(configData['end_date'], "%Y-%m-%d")
        self.in_sample_year_cnt = configData['in_sample_years']
        self.out_sample_year_cnt = configData['out_sample_years']
        self.carry_over_trades = bool(configData['carry_over_trades'])
        self.opt_params = configData['opt_params']
        self.hist_window = configData['hist_window']
        self.min_trades = configData['min_trades']
        self.stop_loss_percent = configData['stop_loss_percent']

    def display(self):
        print('**********  SYSTEM CONFIGURATION PARAMETERS  **********')
        print('Optimization method:     %s' % (self.opt_name))
        print('Optimize metric:         %s' % (self.opt_metric))
        print('Optimize metric ascend:  %s' % (self.opt_metric_asc))
        print('Algorithm name:          %s' % (self.algo_name))
        print('Long only:               %s' % (self.long_only))
        print('Capital base:            %s' % (self.capital_base))
        print('Commission:              %s' % (self.commission))
        print('Start date:              %s' % (self.start_date))
        print('End date:                %s' % (self.end_date))
        print('In-sample years          %s' % (self.in_sample_year_cnt))
        print('Out-sample years         %s' % (self.out_sample_year_cnt))
        print('Carry over trades:       %s' % (self.carry_over_trades))
        print('Benchmark ticker:        %s' % (self.benchmark_ticker))
        print('Historical window:       %s' % (self.hist_window))
        print('Minimum trades:          %s' % (self.min_trades))
        print('Stop loss percent:       %s' % (self.stop_loss_percent))
        print('Tickers & BA spread(s):')
        for key, value in self.tickers_spreads.iteritems():
            print('                         %s: %s' % (key, value))
        print('Hyper parameters:')
        for key, value in self.opt_params.iteritems():
            print('                         %s: %s' % (key, value))
        print('********************************************************')
        print
