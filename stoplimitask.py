#!/usr/bin/env python3
#
# test name: stoplimitask.py
# test author: munair simpson
# test created: 20220815
# test purpose: submit a "stop-limit" sell order to the orderbook using Gemini's REST API.


# Detailed Description:
#  1. Use the losspreventer library to submit a stop-limit order.
#  2. Print the results using the logger library.
#  3. Send an alert to a Discord channel using the messenger library's webhook.
#
# Execution:
#   - Use the wrapper BASH script in the "tests" directory.

import sys
import json

from decimal import Decimal

from libraries.logger import logger
from libraries.informer import maximumbid
from libraries.losspreventer import limitstop
from libraries.messenger import appalert as appalert


# Set trading default trading pair in cause a BASH wrapper has not been used.
pair = 'BTCUSD'
size = '0.00001'
stop = '0.0050'
sell = '0.0100'

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 5:
    pair = sys.argv[1]
    size = sys.argv[2]
    stop = sys.argv[3]
    sell = sys.argv[4]
else: 
    logger.debug ( f'command line parameters improperly specified. using default values for {pair}...' )

# Get the highest bid in the orderbook.
roof = maximumbid( pair )

# JSON not found.
# Response is a price.
# Cast decimal prices.
roof = Decimal( roof )
stop = Decimal( stop )
sell = Decimal( sell )

stop = Decimal( roof * (1 - stop) )
sell = Decimal( roof * (1 - sell) )

# Make sure that the "sell price" is less than "stop price" as required by Gemini.
if Decimal(sell).compare( Decimal(stop) ) == 1:
    notice = f'The sale price {sell} {pair[3:]} cannot be larger than the stop price {stop} {pair[3:]}. '
    logger.debug ( f'{notice}' )
    sys.exit(1)

# Make sure that the "sell price" and the "stop price" are below the market price (ceiling/roof).
if stop.compare( roof ) == 1:
    notice = f'The stop price {stop} {pair[3:]} cannot be larger than the market price ~{roof} {pair[3:]}. '
    logger.debug ( f'{notice}' )
    sys.exit(1)

