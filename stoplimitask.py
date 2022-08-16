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
from libraries.pricegetter import maximumbid
from libraries.losspreventer import limitstop
from libraries.messenger import appalert as appalert
from libraries.definer import ticksizes as ticksizes


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

# Determine tick size.
item = [ item['tick'] for item in ticksizes if item['currency'] == pair[:3] ]
tick = Decimal( item[0] )

# Get the highest bid in the orderbook.
roof = maximumbid( pair )

# JSON not found.
# Response is a price.
# Cast decimal prices.
roof = Decimal( roof )
stop = Decimal( stop )
sell = Decimal( sell )

stop = Decimal( roof * (1 - stop) ).quantize( tick )
sell = Decimal( roof * (1 - sell) ).quantize( tick )

# Record prices in logfile.
logger.debug ( f'roofdump: {roof}' )
logger.debug ( f'stopdump: {stop}' )
logger.debug ( f'selldump: {sell}' )

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

# Get public market data on the lowest ask in the orderbook using the Gemini REST API.
sale = limitstop( str(pair), str(size), str(stop), str(sell) )
if sale:
    fragmentone = f'A stop limit ask order for {size} {pair[:3]} was submitted to the Gemini orderbook. '
    fragmenttwo = f'The stop price was set to {stop} {pair[3:]}. The sell price was set to {sell} {pair[3:]}.'
    logger.info ( f'{fragmentone}{fragmenttwo}')
    appalert ( f'{fragmentone}{fragmenttwo}')

    # Let the shell know we successfully made it this far!
    sys.exit(0)
else: sys.exit(1)