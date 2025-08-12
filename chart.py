# This class - loads data from polygon 
# Transforms data into chart
# outputs chart data

# Main function is return_current_chart as a vector not DICT
# checks date a symbols
# returns the latest chart info for all symbols

# Other functions
# 1. Get latest candels from polygon for all symbols
# 2. Transform data using wavelet transform
# 3. add stat values 

# Process
# For each symbol in symbols:
#   Get latest data from polygon - convert datetime (oldest to newest) asc order
#   denoise data
#   On last symbol add data column
#   Drop na records
#   add to dict 
#
# Return vector not dict
