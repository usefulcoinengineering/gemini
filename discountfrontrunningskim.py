#!/usr/bin/env python3


# Strategy Outline:
#  1. Waiting for a drop in the price of BTC.
#  2. Submit a bid one tick above the best bid (using frontrunner library).
#  3. The bid size is specified in the base currency (BTC).
#  4. Upon execution, immediately submit an ask that includes a small gain (skim).
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json
import requests

from decimal import Decimal

from libraries.logger import logger
from libraries.dealseeker import askfall
from libraries.frontrunner import bidorder
from libraries.liquiditymaker import askorder
from libraries.skimvalidator import confirmexecution


# Set bid size in the base currency (BTC in this case). You will accumulate USD.
# This amount should exceed 20 cents ['0.00001' is the minimum for BTCUSD].
# Configure price drop desired in decimal terms (for example 76 basis points).
# Configure price rise desired in decimal terms (for example 78 basis points).
# Makes sure both price changes, when summed, exceed 20 basis points (or '0.002').
# This covers Gemini API trading fees round trip!
pair = 'BTCUSD'
size = '0.00001'
drop = '0.0076'
rise = '0.0078'

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 5:
    pair = sys.argv[1]
    size = sys.argv[2]
    drop = sys.argv[3]
    rise = sys.argv[4]

# Open websocket connection.
# Wait for asks to fall in price.
logger.info(f'waiting for {pair} to drop {Decimal(drop)*100}% in price to buy {size} {pair[:3]}..')
deal = askfall( pair, drop )
if deal:

    # Submit limit bid order.
    logger.debug(f'submitting {pair} frontrunning limit bid order.')
    post = bidorder( pair, size )
    post = post.json()
    dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( dump )

    # Define poststatus class.
    # Purpose: Stores the state of the orderid parameter upon exiting the websocket connection session.
    class Poststatus:
        def __init__(self, state): self.__state = state
        def getvalue(self): return self.__state
        def setvalue(self, state): self.__state = state

    # Define bidpricing class.
    # Purpose: Stores the state of the filled bid price parameter upon exiting the websocket connection session.
    class Bidpricing:
        def __init__(self, state): self.__state = state
        def getvalue(self): return self.__state
        def setvalue(self, state): self.__state = state

    # Initialize poststatus and bidpricing values.
    poststatus = Poststatus('')
    bidpricing = Bidpricing('')

    # Determine if the bid order was filled.
    confirmexecution( orderid = post['order_id'], poststatus = poststatus, bidpricing = bidpricing )
    if 'filled' in poststatus.getvalue(): poststatus = True
    if poststatus:
        minimumask = Decimal( bidpricing.getvalue() )

        # Calculate ask price (skim/premium).
        gain = 1 + Decimal(rise)
        skim = Decimal( minimumask * gain ).quantize( Decimal('0.00') )
        skim = str( skim )

        # Submit limit ask order.
        logger.debug(f'submitting {pair} limit ask order: {skim} ask for {size} {pair[:3]}..')
        post = askorder( pair, size, skim )
        post = post.json()
        dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
        logger.debug ( dump )

        # Reset poststatus value.
        poststatus = Poststatus('')

        # Determine if the ask order was filled.
        confirmexecution( orderid = post['order_id'], poststatus = poststatus, bidpricing = bidpricing )
        if 'filled' in poststatus.getvalue(): poststatus = True

        # Let the shell know we successfully made it this far!
        sys.exit(0)

    else: sys.exit(1)
