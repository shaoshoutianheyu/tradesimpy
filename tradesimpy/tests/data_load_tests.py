from tests_import import *
import unittest
import Quandl
from pprint import pprint


QUANDL_API_KEY = 'B8h6uA58skuqwcAtL_tf'


class DataLoadTests(unittest.TestCase):
    def TestLoadingStockData(self):
        data = Quandl.get("FRED/GDP", authtoken=QUANDL_API_KEY)

if __name__ == '__main__':
    unittest.main()
