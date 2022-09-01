#!/usr/bin/env python3
#
# script name: trademonitor.py
# script author: munair simpson
# script created: 20220831
# script purpose: use websockets to continually monitor the trading range of a trading pair.

# Detailed Description:
#  1. Use the marketmonitor library to request the required information.
#  2. Print the results using the logger library.
#  3. Send an alert to a Discord channel using the messenger library's webhook.
#
# Execution:
#   - Use the wrapper BASH script in the "tests" directory.

import json
import sys
import asyncio

from libraries.logger import logger
from libraries.trademonitor import blockpricerange

# Set default trading pair and loop exit price in case a BASH wrapper has not been used.
marketpair = "ETHUSD"
upperbound = "1500"
lowerbound = "1400"

# Override defaults with command line parameters from BASH wrapper.
if len ( sys.argv ) == 4 :
    marketpair = sys.argv[1]
    upperbound = sys.argv[2]
    lowerbound = sys.argv[3]
else :
    logger.warning ( f'incorrect number of command line arguments. using default values...' )
    logger.warning ( f'marketpair: {marketpair}' )
    logger.warning ( f'upperbound: {upperbound}' )
    logger.warning ( f'lowerbound: {lowerbound}' )


try : # Enter price monitor loop.
    messageresponse = asyncio.run (
    blockpricerange (
            marketpair, 
            upperbound, 
            lowerbound 
        )
    )
except KeyboardInterrupt :
    pass

logger.debug ( messageresponse )
logger.info ( f'{messageresponse} is out of bounds. ') # Report status.
logger.debug ( messageresponse["price"] )
logger.info ( f'{messageresponse["price"]} is out of bounds. ') # Report status.

sys.exit ( 0 )