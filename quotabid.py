#!/usr/bin/env python3


# Strategy Outline:
#  1. Want to purchase DAI at a specific price.
#  2. The bid size is limited by a USD (quote currency) budget.
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json
import requests

from decimal import Decimal

from libraries.logger import logger
from libraries.liquiditymaker import quotabid
from libraries.fillvalidator import confirmexecution


# Set the pair.
# Set quote currency (USD in this case) budget.
# Set your price reservation.
pair = 'DAIUSD'
cash = '100'
cost = '1.00913'

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 4:
    pair = sys.argv[1]
    cash = sys.argv[2]
    drop = sys.argv[3]

# Submit limit bid order.
logger.debug(f'submitting {pair} limit bid order: {cost} bid on a {cost} budget.')
post = quotabid( pair, cash, cost )
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
