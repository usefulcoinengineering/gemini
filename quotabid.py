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
