import os
import sys

# Provide directory paths for necessary imports
lib_paths =\
    [
        os.path.abspath('../engines/'),
        os.path.abspath('../configurations/')
    ]

for lib_path in lib_paths:
    sys.path.append(lib_path)
