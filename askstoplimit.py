#!/usr/bin/env python3
#
# script name: askstoplimit.py
# script author: munair simpson
# script created: 20220815
# script purpose: submit a "stop-limit" sell order to the orderbook using Gemini's REST API.


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
from libraries.stopper import askstoplimit
from libraries.pricegetter import ticker
from libraries.definer import ticksizes as ticksizes
from libraries.messenger import sendmessage as sendmessage

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
last = ticker( pair )["bid"]

# JSON not found.
# Response is a price.
# Cast decimal prices.
last = Decimal( last )
stop = Decimal( stop )
sell = Decimal( sell )

stop = Decimal( last * (1 - stop) ).quantize( tick )
sell = Decimal( last * (1 - sell) ).quantize( tick )

# Record prices in logfile.
logger.debug ( f'Last Price: {last}' )
logger.debug ( f'Stop Price: {stop}' )
logger.debug ( f'Sell Price: {sell}' )

# Make sure that the "sell price" is less than "stop price" as required by Gemini.
if Decimal(sell).compare( Decimal(stop) ) == 1:
    notice = f'The sale price {sell} {pair[3:]} cannot be larger than the stop price {stop} {pair[3:]}. '
    logger.debug ( f'{notice}' )
    sys.exit(1)

# Make sure that the "sell price" and the "stop price" are below the market price (ceiling/last).
if stop.compare( last ) == 1:
    notice = f'The stop price {stop} {pair[3:]} cannot be larger than the market price ~{last} {pair[3:]}. '
    logger.debug ( f'{notice}' )
    sys.exit(1)

# Submit stop sell order to the orderbook using the Gemini REST API.
response = askstoplimit( str(pair), str(size), str(stop), str(sell) ).json()

# Remove comments to debug: 
# logger.debug ( json.dumps( response, sort_keys=True, indent=4, separators=(',', ': ') ) )

try:    
    if response["is_live"] : 
        fragmentone = f'Order {response["order_id"]} for {size} {pair[:3]} was submitted to the Gemini orderbook. '
        fragmenttwo = f'The stop price was set to {stop} {pair[3:]}. The sell price was set to {sell} {pair[3:]}.'
        logger.info ( f'{fragmentone}{fragmenttwo}')
        sendmessage ( f'{fragmentone}{fragmenttwo}')

        # Exit 0
        sys.exit(0)

# Return response.
except KeyError as e:
    logger.warning ( f'KeyError: {e}' )
    sendmessage ( "Unsuccessful stop limit order submission." )

try:    
    if response["result"] : sendmessage ( f'\"{response["reason"]}\" {response["result"]}: {response["message"]}' )

# Return response.
except KeyError as e:
    logger.critical ( f'KeyError: {e}' )
    sendmessage ( "Unexpecter error. Unsuccessful stop limit order submission." )
    sys.exit(1)

