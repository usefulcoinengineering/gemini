#!/usr/bin/env python3
#
# test name: islive.py
# test author: munair simpson
# test created: 20220816
# test purpose: check order number specified is active on the orderbook (i.e. has remaining size and has not been canceled).


# Detailed Description:
#  1. Use the informer library to request the required information.
#  2. Print the results using the logger library.
#  3. Send an alert to a Discord channel using the messenger library's webhook.
#
# Execution:
#   - Use the wrapper BASH script in the "tests" directory.

import sys

from libraries.logger import logger
from libraries.orderchecker import islive
from libraries.messenger import appalert as appalert


# Set trading default trading pair in cause a BASH wrapper has not been used.
order = 136457975606

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 2:
    order = sys.argv[1]

# Get public market data on the highest bid in the orderbook using the Gemini REST API.
orderstatus = islive( order )

# Report the response if there is one.
if order:
    # Tell the user the result.
    alertmessage = f'Order {order} is live on the Gemini orderbook. '
    logger.debug = f'{alertmessage}' ; appalert ( f'{alertmessage}')

    # Let the shell know we successfully made it this far!
    sys.exit(0)

else: 
    # Tell the user the result.
    alertmessage = f'Order {order} is NOT live on the Gemini orderbook. '
    logger.debug = f'{alertmessage}' ; appalert ( f'{alertmessage}')

    # Let the shell know that the desired output was not received.
    sys.exit(1)
