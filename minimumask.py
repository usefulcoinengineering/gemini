#!/usr/bin/env python3
#
# script name: minimumask.py
# script author: munair simpson
# script created: 20220811
# script purpose: retrieve public market data on the lowest ask in the orderbook using Gemini's REST API.


# Detailed Description:
#  1. Use the informer library to request the required information.
#  2. Print the results using the logger library.
#  3. Send an alert to a Discord channel using the messenger library's webhook.
#
# Execution:
#   - Use the wrapper BASH script in the "tests" directory.

import sys

from libraries.logger import logger
from libraries.pricegetter import minimumask
from libraries.messenger import sendmessage as sendmessage


# Set trading default trading pair in cause a BASH wrapper has not been used.
pair = 'BTCUSD'

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 2:
    pair = sys.argv[1]

# Get public market data on the lowest ask in the orderbook using the Gemini REST API.
cost = minimumask( pair )

# Report the response if there is one.
if cost:
    # Tell the user the result.
    fragmentone = f'The lowest ask for {pair[:3]} in the Gemini orderbook is: '
    fragmenttwo = f'{cost} {pair[3:]}.'
    logger.info ( f'{fragmentone}{fragmenttwo}')
    sendmessage ( f'{fragmentone}{fragmenttwo}')

    # Let the shell know we successfully made it this far!
    sys.exit(0)

else: sys.exit(1)
