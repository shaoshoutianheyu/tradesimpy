import sys
import json
from global_import.zipline_import import *
from backtester_import import *

def main(args):
    configFile = args[0]

    # Extract data from config (JSON) file
    with open(configFile, mode='r') as f:
        configData = json.loads(f.read())

    # Read in config parameters
    optName = configData['opt_method'].lower()
    assetCount = configData['asset_count'].lower()
    strategyType = configData['strategy_type'].lower()
    strategyName = configData['strategy_name'].lower()
    tickers = configData['tickers']
    startDate = configData['start_date']
    endDate = configData['end_date']
    inSampleDays = int(configData['in_sample_days'])
    outSampleDays = int(configData['out_sample_days'])
    optParams = configData['opt_params']

    # Display inputted config parameters
    print '**********  BACKTEST CONFIGURATION PARAMETERS  **********'
    print 'Optimization method:     %s' % (optName)
    print 'Asset count:             %s' % (assetCount)
    print 'Strategy type:           %s' % (strategyType)
    print 'Strategy name:           %s' % (strategyName)
    print 'Start date:              %s' % (startDate)
    print 'End date:                %s' % (endDate)
    print 'In-sample day count:     %s' % (inSampleDays)
    print 'Out-of-sample day count: %s' % (outSampleDays)
    print 'Ticker(s):'
    for ticker in tickers:
        print '                         %s' % (ticker)
    print 'Hyper parameters:'
    for key, value in optParams.iteritems():
        print '                         %s : %s' % (key, value)
    print '*********************************************************'
    print

    # TODO: Check if ticker(s) existed during period needed for backtesting
    # for ticker in tickers:
    #     sec = symbol("SPY")
        # if sec.security_start_date > startDate:
        #     print 'ERROR: %s started trading %d and the backtest requires data up to %s' % \
        #           (sec.security_start_date, startDate)
        #
        # print '%s:          %s' % (sec.symbol, sec.security_start_date)
        # print 'Backtest:    %s' % (startDate)

    # Construct list of date ranges for in-sample and out-of-sample periods
    samplePeriods = CreateSampleTestingPeriods(startDate, endDate, inSampleDays, outSampleDays)

    # Display sample period date ranges
    print 'Sample periods:'
    for sp in samplePeriods:
        print '    In:  %s - %s (%d)' % (sp['in'][0].date(), sp['in'][1].date(), (sp['in'][1] - sp['in'][0]).days)
        print '    Out: %s - %s (%d)' % (sp['out'][0].date(), sp['out'][1].date(), (sp['out'][1] - sp['out'][0]).days)
        print

    # Determine which trading strategy to implement
    print 'Creating trading algorithm...'
    tradingStrategy = CreateTradingStrategy(assetCount, strategyType, strategyName)
    print 'Created trading algorithm!\n'

    # Determine which optimizer to implement
    print 'Creating optimizer...'
    optimizer = CreateOptimizer(optName, optParams, tradingStrategy, tickers)
    print 'Created optimizer!\n'

    # Display to user total number of optimizations per timestep
    print 'There will be %d distinct scenarios per optimization step\n' % (optimizer.numParamSets)

    # Begin backtesting trading strategy
    for periods in samplePeriods:
        inStart = periods['in'][0]
        inEnd = periods['in'][1]
        outStart = periods['out'][0]
        outEnd = periods['out'][1]

        # Optimize over in-sample data
        print 'Starting in-sample optimization for dates %s to %s.\n' % (inStart.date(), inEnd.date())
        optResults = optimizer.Run(inStart, inEnd)
        print '\nFinished in-sample optimization for dates %s to %s.\n' % (inStart.date(), inEnd.date())
        # print optResults

        # Simulate over out-of-sample data
        print 'Starting out-of-sample simulation for dates %s to %s.\n' % (outStart.date(), outEnd.date())

        print '\nFinished out-of-sample simulation for dates %s to %s.\n' % (outStart.date(), outEnd.date())

        # Record results for later analysis


        break

def CreateTradingStrategy(assetCount, strategyType, strategyName):
    if assetCount == 'single':

        if strategyType == 'watermark':

            if strategyName == 'sobel':
                return Sobel_SingleWatermark()
            else:
                print 'ERROR: Unknown strategy name %s' % (strategyName)
                exit(1)

        elif strategyType == 'updown':
            pass
        elif strategyType == 'divergence':
            pass
        else:
            print 'ERROR: Unknown strategy type %s' % (strategyType)
            exit(1)

    elif assetCount == 'multi':

        if strategyType == 'watermark':
            pass
        elif strategyType == 'updown':
            pass
        elif strategyType == 'divergence':
            pass
        else:
            print 'ERROR: Unknown strategy type %s' % (strategyType)
            exit(1)

    else:
        print 'ERROR: Unknown asset count %s' % (assetCount)
        exit(1)

def CreateOptimizer(optName, optParams, tradingStrategy, tickers):
    if optName == 'grid search':
        return GridSearchOptimizer(tradingStrategy, optParams, tickers)
    else:
        print 'ERROR: Unknown optimizer %s' % (optName)
        exit(1)

def CreateSampleTestingPeriods(startDate, endDate, inSampleDays, outSampleDays):
    samplePeriods = []

    # Full sample period
    startDateTime = pd.datetime.strptime(startDate, "%Y-%m-%d")
    endDateTime = pd.datetime.strptime(endDate, "%Y-%m-%d")

    # Determine and store all sample periods
    while (startDateTime + BDay(outSampleDays - 1)) <= endDateTime:
        inStart = startDateTime - BDay(inSampleDays)
        inEnd = startDateTime - BDay(1)
        outStart = startDateTime
        outEnd = startDateTime + BDay(outSampleDays - 1)

        samplePeriods.append(
            {
                'in':   [inStart, inEnd],
                'out':  [outStart, outEnd]
            }
        )

        # Update new start date
        startDateTime = startDateTime + BDay(outSampleDays)

    # Be sure to include any remaining days in full sample period as a sample period
    if startDateTime < endDateTime:
        samplePeriods.append(
            {
                'in':   [startDateTime - BDay(inSampleDays), startDateTime - BDay(1)],
                'out':  [startDateTime, endDateTime]
            }
        )

    return samplePeriods

if __name__ == '__main__':
    # if len(sys.argv) != 4:
    #     print('Please provide valid parameters {[algorithm name] [optimization name] [fast backtest (true/false)]}')
    #     exit(1)
    if len(sys.argv) != 2:
        print('Please provide valid parameters {[configuration file]}')
        exit(1)

    main(sys.argv[1:])