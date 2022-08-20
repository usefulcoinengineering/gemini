#!/usr/bin/env python3
#
# script name: trailingstop.py
# script author: munair simpson
# script created: 20220816
# script purpose: buy the specified asset then sell it using a highest bid trailing stop-limit ask.


# Strategy Outline:
#  1. Buy BTC (by default) almost at the market price using the REST API (with a frontrunning USD bid).
#  2. Open a websocket connection and wait for confirmation that submitted bid order was filled.
#  3. Capture the price of the exexuted order and use it to calculate the last price that should trip the submission of a stop-limit order.
#  4. Monitor last price data in trade messages and do nothing until the transaction price exceeds the trip price.
#  5. On the first occassion that last price exceeds the trip price submit a stop-limit order to market sell when the "stop" is reached.
#  6. Whenever last price exceeds the session high update/adjust the stop-limit order upwards.
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json

from decimal import Decimal

import libraries.definer as definer

from libraries.logger import logger
from libraries.ordermanager import islive
from libraries.frontrunner import bidorder
from libraries.stopper import askstoplimit
from libraries.marketmonitor import bidrise
from libraries.ordermanager import cancelorder
from libraries.volumizer import notionalvolume
from libraries.definer import ticksizes as ticksizes
from libraries.closevalidator import confirmexecution
from libraries.messenger import sendmessage as sendmessage

# Set bid size in the base currency (BTC in this case).
# This amount should exceed ~25 cents ['0.00001' is the minimum for BTCUSD].
# You will accumulate gains in the quote currency (USD in this case). This amount is called the "quotegain".
# Specify the percentage discount off the market price that determines the stop price desired in decimal terms (for example 100 basis points).
# Specify the percentage discount off the market price that determines the sell price desired in decimal terms (for example 200 basis points).
# Makes sure both price deltas, exceed the Gemini API fee if you want this to execute profitably. For example, 20 basis points (or '0.002').
pair = 'BTCUSD'
size = '0.00001'
stop = '0.0100'
sell = '0.0200'

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 5:
    pair = sys.argv[1]
    size = sys.argv[2]
    stop = sys.argv[3]
    sell = sys.argv[4]
else: 
    logger.warning ( f'incorrect number of command line arguments. using default values for {pair} trailing...' )

# Cast decimals.
size = Decimal(size)
stop = Decimal(stop)
sell = Decimal(sell)

# Make sure "sell" is more than "stop".
# Gemini requires this for stop ask orders:
# The stop price must exceed the sell price.
if stop.compare( sell ) == 1:
    notification = f'The sell price discount {sell} cannot be larger than the stop price discount {stop}. '
    logger.error ( f'{notification}' )
    sys.exit(1)

# Determine tick size.
item = [ item['tick'] for item in ticksizes if item['currency'] == pair[:3] ]
tick = Decimal( item[0] )

# Determine Gemini API transaction fee.
jsonresponse = notionalvolume().json()
geminiapifee = jsonresponse["api_maker_fee_bps"]

# Submit limit bid order and dump the JSON response in the logs.
logger.debug ( f'Submitting {pair} frontrunning limit bid order.' )
jsonresponse = bidorder( pair, size ).json()
logger.debug ( json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(',', ': ') ) )
