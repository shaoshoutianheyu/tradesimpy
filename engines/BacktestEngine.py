from backtest_engine_import import *
from BacktestConfiguration import BacktestConfiguration
from Backtester import Backtester
import json
import pandas as pd


class BacktestEngine(object):
    def __init__(self, config_uri):
        self.config = parse_config(config_uri)

    def parse_config(self, config):
        # Read JSON
        with open(configFile, mode='r') as f:
            config_data = json.loads(f.read())

        # Create a backtest configuration
        return BacktestConfiguration(
            config_data['algorithm_name'].lower(),
            pd.datetime.strptime(config_data['start_date'], "%Y-%m-%d"),
            pd.datetime.strptime(config_data['end_date'], "%Y-%m-%d"),
            float(config_data['cash']),
            config_data['time_resolution'].lower(),
            config_data['tickers'],
            config_data['ticker_types'],
            config_data['ticker_series_names'],
            config_data['data_sources'],
            float(config_data['commission']),
            config_data['algorithm_parameters'])

    def run(self, data):
        pass
        # TODO: Check if all data is present


        # TODO: Create the trading algorithm


        # TODO: Setup and run the backtester
        # backtester = Backtester()
        # results = backtester.run()
