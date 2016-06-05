import pandas as pd
import numpy as np

def discrete_returns(price_series):
    return price_series / price_series.shift(1) - 1

def log_returns(price_series):
    return price_series.log() - price_series.log()

def annualization_factor(frequency):
    frequency = frequency.lower()
    
    if(frequency == 'daily'):
        return 252
    elif(frequency == 'weekly'):
        return 52
    elif(frequency == 'monthly'):
        return 12
    elif(frequency == 'quarterly'):
        return 4
    elif(frequency == 'yearly'):
        return 1
    else:
        raise NotImplementedError("The frequency %s is not supported." % frequency)

def sharpe_ratio(return_series, frequency):
    factor = annualization_factor(frequency)

    return np.sqrt(factor) * return_series.mean() / return_series.std()
