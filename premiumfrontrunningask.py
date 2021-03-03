#!/usr/bin/env python3


# Strategy Outline:
#  1. Waiting for a rise in the price of YFI.
#  2. Submit an ask one tick below the best ask (using frontrunner library).
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json
import requests

from decimal import Decimal

from libraries.logger import logger
from libraries.rentseeker import bidrise
from libraries.frontrunner import askorder
from libraries.fillvalidator import confirmexecution


# Set quote currency (USD in this case) budget.
# This amount should exceed 20 cents ['0.00001' is the minimum for YFIUSD].
# Configure price rise desired in decimal terms.
# For example, 20 basis points is '0.002'. This covers Gemini API trading fees round trip!
pair = 'YFIUSD'
size = '0.07765'
rise = '0.005'

# Override defaults with command line parameters.
if len(sys.argv) == 4:
    pair = sys.argv[1]
    size = sys.argv[2]
    rise = sys.argv[3]

# Open websocket connection.
# Wait for bids to rise in price.
logger.info(f'waiting for {pair} to rise {Decimal(rise)*100}% in price to sell {size} {pair[3:]} worth..')
deal = bidrise( pair, rise )
if deal:

    # Submit limit ask order.
    logger.debug(f'submitting {pair} frontrunning limit ask order.')
    post = askorder( pair, size )
    post = post.json()
    dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( dump )

    # Define poststatus class.
    # Purpose: Stores the state of the orderid parameter upon exiting the websocket connection session.
    class Poststatus:
        def __init__(self, state): self.__state = state
        def getvalue(self): return self.__state
        def setvalue(self, state): self.__state = state

    poststatus = Poststatus('')

    # Determine if the order was filled.
    confirmexecution( orderid = post['order_id'], poststatus = poststatus )
    if 'filled' in poststatus.getvalue(): poststatus = True

    # Let the shell know we successfully made it this far!
    if poststatus: sys.exit(0)
    else: sys.exit(1)
