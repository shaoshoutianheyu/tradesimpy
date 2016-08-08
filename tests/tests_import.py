import os
import sys

# Provide directory paths for necessary imports
lib_paths =\
    [
        os.path.abspath('../tradesimpy/'),
        os.path.abspath('../tradesimpy/data/'),
        os.path.abspath('../tradesimpy/engines/'),
        os.path.abspath('../tradesimpy/backtester/'),
        os.path.abspath('../tradesimpy/optimizers/'),
        os.path.abspath('../tradesimpy/optimizers/analytics/'),
        os.path.abspath('../tradesimpy/walk_forward_analyzer/'),
        os.path.abspath('../tradesimpy/configurations/'),
        os.path.abspath('../tradesimpy/trading_algorithm/'),
    ]

for lib_path in lib_paths:
    sys.path.append(lib_path)

sys.path = list(set(sys.path))
