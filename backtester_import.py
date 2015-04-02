import os
import sys

# Provide directory paths for necessary imports
lib_paths =\
    [
        os.path.abspath('./optimizers/'),
        os.path.abspath('./trading_algorithms/watermark/'),
        os.path.abspath('./trading_algorithms/updown/'),
        os.path.abspath('./trading_algorithms/divergence/')
    ]

for lib_path in lib_paths:
    sys.path.append(lib_path)
