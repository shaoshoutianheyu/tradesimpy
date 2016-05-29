import os
import sys

# Provide directory paths for necessary imports
lib_paths =\
    [
        os.path.abspath('../data/'),
        os.path.abspath('../backtester/'),
        os.path.abspath('../trading_algorithm/'),
    ]

for lib_path in lib_paths:
    sys.path.append(lib_path)

sys.path = list(set(sys.path))
