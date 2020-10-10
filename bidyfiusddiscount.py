#!/usr/bin/env python3


# Strategy Outline:
#  1. Waiting for a drop in the price of YFI.
#  2. Submit a bid one tick below the best ask.
#  3. The bid size is limited by a USD (quote currency) budget.
#
# Execution:
#   - Copy this file from the strategies directory to the level below. Run with python3.

import json
import requests

from decimal import Decimal

from libraries.logger import logger
from libraries.dealseeker import askfall
from libraries.spreadkiller import quotabid
from libraries.fillvalidator import confirmexecution


# Set quote currency (USD in this case) budget.
# This amount should exceed 20 cents ['0.00001' is the minimum for YFIUSD].
# Configure price drop desired in decimal terms.
# For example, 20 basis points is '0.002'. This covers Gemini API trading fees round trip!
pair = 'YFIUSD'
cash = '0.25'
drop = '0.00'

# Open websocket connection.
# Wait for asks to fall in price.
logger.info(f'waiting for {pair} to drop {Decimal(drop)*100}% in price to buy {cash} {pair[3:]} worth..')
deal = askfall( pair, drop )
if deal:

    # Submit limit bid order.
    logger.debug(f'submitting {pair} aggressive limit bid order.')
    post = quotabid( pair, cash )
    post = post.json()
    dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( dump )

    # Define poststatus class.
    # Purpose: Stores the state of the orderid parameter upon exiting the websocket connection session.
    class Poststatus:
        def __init__(self, state): self.__state = state
        def getvalue(self): return self.__state
        def setvalue(self, state): self.__state = state

    poststatus = Poststatus(False)

    # Determine if the order was filled.
    confirmexecution( orderid = post['order_id'], poststatus = poststatus )
