#!/usr/bin/env python3
#
# script name: priceincreasemonitor.py
# script author: munair simpson
# script created: 20220818
# script purpose: use websockets to continually monitor a trading pair for an increase in price levels.

# Detailed Description:
#  1. Use the takermonitor library to request the required information.
#  2. Print the results using the logger library.
#  3. Send an alert to a Discord channel using the messenger library's webhook.
#
# Execution:
#   - Use the wrapper BASH script in the "tests" directory.

import sys

from libraries.logger import logger
from libraries.marketmonitor import priceincrease

# Set default trading pair and loop exit price in case a BASH wrapper has not been used.
pair = "ETHUSD"
exit = "2400"

# Override defaults with command line parameters from BASH wrapper.
if len( sys.argv ) == 3 :
    pair = sys.argv[1]
    exit = sys.argv[2]
else :
    logger.warning ( f'incorrect number of command line arguments. using default values of a {exit} price level for {pair}...' )

# Enter price monitor loop.
orderstatus = priceincrease( pair=pair, exit=exit )
if orderstatus : sys.exit( 0 )
else : sys.exit( 1 )