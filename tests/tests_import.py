import os
import sys

# Provide directory paths for necessary imports
lib_paths =\
    [
        os.path.abspath('../tradesimpy/'),
        os.path.abspath('../tradesimpy/data/'),
        os.path.abspath('../tradesimpy/configurations/'),
    ]

for lib_path in lib_paths:
    sys.path.append(lib_path)

sys.path = list(set(sys.path))
