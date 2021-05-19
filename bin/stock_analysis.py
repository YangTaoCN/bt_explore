# A function that shows a specific stock analization.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
sys.path.append('strategies')
import sma_optimized
import automatic

def stock_analysis(stock, from_date, to_date):
    sma_optimized.stock_analysis(stock, from_date, to_date)
    #automatic.stock_analysis(stock, from_date, to_date)