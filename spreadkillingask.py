#!/usr/bin/env python3


# Strategy Outline:
#  1. Urgently need to sell DAI.
#  2. Submit an ask one tick above the best bid.
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json
import requests

from decimal import Decimal

from libraries.logger import logger
from libraries.spreadkiller import askorder
from libraries.fillvalidator import confirmexecution


# Set bid size ['0.1' is the minimum for DAIUSD].
pair = 'DAIUSD'
size = '0.1'

# Override defaults with command line parameters.
if len(sys.argv) == 3:
    pair = sys.argv[1]
    size = sys.argv[2]

# Submit limit bid order.
logger.debug(f'submitting {pair} aggressive limit bid order.')
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
