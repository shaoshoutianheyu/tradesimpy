import numpy as np
import scipy as sp
from scipy import stats, signal, ndimage


def sobel_operator(data, params):
    # Initialize parameters and structures
    sigma = params['sigma']
    delay = params['delay']
    edge = np.empty(shape=data.shape)

    # Filter data and implement Sobel operator
    filtered_data = ndimage.filters.gaussian_filter1d(data.values, sigma)
    ndimage.sobel(input=filtered_data, output=edge, mode="reflect")

    return edge[-delay]

def least_squares_angle(data, params):
    # Initialize parameters and structures
    sigma = params['sigma']
    window = params['window']
    windowed_data = data.values[-window:]
    t = np.arange(len(windowed_data))

    # Filter data, retrieve regression, and determine angle of regression line
    filtered_data = ndimage.filters.gaussian_filter1d(windowed_data, sigma)
    slope, intercept, r_value, p_value, std_err = stats.linregress(t, filtered_data)
    angle = 180*np.arctan(slope)/np.pi

    return angle
