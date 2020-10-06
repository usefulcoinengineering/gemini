#!/usr/bin/env python3


# Strategy Outline:
#  1. Urgently need DAI.
#  2. Submit a bid one tick below the best ask.
#
# Execution:
#   - Copy this file from the strategies directory to the level below. Run with python3.

import json
import requests

from decimal import Decimal

from libraries.logger import logger
from libraries.spreadkiller import bidding
from libraries.fillvalidator import confirmexecution


# Set bid size ['0.001' is the minimum for ETHUSD].
# Define pair and price drop desired (at least 2X fees).
# Price depreciation defined in decimals (0.1 is 10%).
pair = 'DAIUSD'
size = '1'

# Submit limit bid order.
logger.info(f'submitting {pair} aggressive limit bid order.')
post = bidding( pair, size )
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
