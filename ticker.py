#!/usr/bin/env python3
#
# script name: ticker.py
# script author: munair simpson
# script created: 20220811
# script purpose: retrieve public market data on the pair specified from the orderbook using Gemini's REST API.


# Detailed Description:
#  1. Use the informer library to request the required information.
#  2. Print the results using the logger library.
#  3. Send an alert to a Discord channel using the messenger library's webhook.
#
# Execution:
#   - Use the wrapper BASH script in the "tests" directory.

import sys
import time

from libraries.logger import logger
from libraries.pricegetter import ticker

# Set trading default trading pair in cause a BASH wrapper has not been used.
pair = 'BTCUSD'

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 2 :
    pair = sys.argv[1]
else : 
    logger.debug ( f'Incorrect number of command line arguments. Specify a trading pair like: {pair.upper()}' )
    exit(1)

# Get public market data on the latest prices in the orderbook using pricegetter wrapper library for the Gemini REST API.
while True:
    try:
        # Get latest ticker.
        # You can only sell for less.
        tickerjson = ticker( pair )
    except Exception as e:
        logger.debug( f'An exception occured when trying to retrieve the price ticker. Error: {e}' )
        time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
        continue
    break

logger.info ( tickerjson )

# Let the shell know we successfully made it this far!
sys.exit(0)