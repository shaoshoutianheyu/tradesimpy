from walk_forward_analysis_engine_import import *
from WalkForwardAnalysisConfiguration import WalkForwardAnalysisConfiguration
from WalkForwardAnalyzer import WalkForwardAnalyzer
import Backtester as b
import trading_algorithms.TradingAlgorithmFactory as taf
import optimizer_factory as of
import data.market_data as market_data
import exceptions as ex
from pprint import pprint


class WalkForwardAnalysisEngine(object):

    def __init__(self):
        pass

    def run(self, config):
        # Estimate data count needed prior to first out-of-sample period
        freq_factor = self._frequency_diff_factor(config.time_resolution, config.sample_period)
        data_request_history_window = (config.in_sample_periods * freq_factor) + config.history_window

        # Load market data
        data = market_data.load_market_data(config.tickers, config.ticker_types, config.data_sources, \
            config.start_date, config.end_date, data_request_history_window)

        # Create the trading algorithm w/o parameters
        trading_algorithm = taf.create_trading_algorithm(config.algorithm_name, config.tickers, config.history_window)

        # Create the optimizer
        optimizer = of.create_optimizer(config.num_processors, config.optimizer_name, trading_algorithm, config.commission, \
            config.ticker_spreads, config.optimization_metric, config.optimization_metric_ascending, config.optimization_parameters)

        # Create the backtester
        backtester = b.Backtester(-1, trading_algorithm, config.cash, config.commission, config.ticker_spreads)

        # Setup and run the walk forward analyzer
        walk_forward_analyzer = WalkForwardAnalyzer(config.in_sample_periods, config.out_of_sample_periods, config.sample_period, \
            optimizer, backtester)

        print('Running the walk forward analyzer...')
        walk_forward_analyzer.run(config.start_date, config.end_date, data)
        print('Ran walk forward analyzer!')
        print

        return walk_forward_analyzer.results

    def _frequency_diff_factor(self, time_resolution, sample_period):
        time_resolution = time_resolution.lower()
        sample_period = sample_period.lower()

        if(time_resolution == 'daily'):
            if(sample_period == 'daily'):
                return 1
            elif(sample_period == 'weekly'):
                return 5
            elif(sample_period == 'monthly'):
                return 21
            elif(sample_period == 'quarterly'):
                return 63
            elif(sample_period == 'yearly'):
                return 252
            else:
                ex.AttributeError.message('ERROR: The sample period provided is not supported.')
        elif(time_resolution == 'weekly'):
            if(sample_period == 'weekly'):
                return 1
            elif(sample_period == 'monthly'):
                return 4
            elif(sample_period == 'quarterly'):
                return 13
            elif(sample_period == 'yearly'):
                return 52
            else:
                ex.AttributeError.message('ERROR: The sample period provided is not supported.')
        elif(time_resolution == 'monthly'):
            if(sample_period == 'monthly'):
                return 1
            elif(sample_period == 'quarterly'):
                return 3
            elif(sample_period == 'yearly'):
                return 12
            else:
                ex.AttributeError.message('ERROR: The sample period provided is not supported.')
        elif(time_resolution == 'quarterly'):
            if(sample_period == 'quarterly'):
                return 1
            elif(sample_period == 'yearly'):
                return 4
            else:
                ex.AttributeError.message('ERROR: The sample period provided is not supported.')
        elif(time_resolution == 'yearly'):
            if(sample_period == 'yearly'):
                return 1
            else:
                ex.AttributeError.message('ERROR: The sample period provided is not supported.')
        else:
            ex.AttributeError.message('ERROR: The time resolution provided is not supported.')

