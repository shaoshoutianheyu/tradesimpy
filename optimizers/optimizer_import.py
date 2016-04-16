import os
import sys

# Provide directory paths for necessary imports
lib_paths =\
    [
        os.path.abspath('../'),
        os.path.abspath('../trading_algorithms/')
        os.path.abspath('./analytics/'),
    ]

for lib_path in lib_paths:
    sys.path.append(lib_path)

sys.path = list(set(sys.path))
