#!/usr/bin/env python3
#
# script name: frontrunningbidtrailingstop.py
# script author: munair simpson
# script created: 20220814
# script purpose: buy the specified asset almost at market with a frontrunning bid then sell it using a trailing stop-limit ask.


# Strategy Outline:
#  1. Buy BTC (by default) almost at the market price using the REST API.
#  2. Open a websocket connection and wait for that submitted bid order to be filled.
#  3. Capture the price of the exexuted order and use it to calculate the last price that should trip the submission of a stop-limit order.
#  4. Monitor last price data in trade messages and do nothing until the transaction price exceeds the trip price.
#  5. On the first occassion that last price exceeds the trip price submit a stop-limit order to market sell when the "stop" is reached.
#  6. Whenever last price exceeds the session high update/adjust the stop-limit order upwards.
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json
import requests

from decimal import Decimal

import libraries.definer as definer

from libraries.logger import logger
from libraries.rentseeker import bidrise
from libraries.frontrunner import bidorder
from libraries.liquiditymaker import askorder
from libraries.losspreventer import limitstop
from libraries.skimvalidator import confirmexecution
from libraries.messenger import appalert as appalert


# Set bid size in the base currency (BTC in this case). You will accumulate USD.
# This amount should exceed 20 cents ['0.00001' is the minimum for BTCUSD].
# Configure price trip desired in decimal terms (for example 200 basis points).
# Configure stop price desired in decimal terms (for example 100 basis points).
# Makes sure both price deltas, exceed the Gemini API fee. For example, 20 basis points (or '0.002').
pair = 'BTCUSD'
size = '0.00001'
trip = '0.0200'
stop = '0.0100'

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 5:
    pair = sys.argv[1]
    size = sys.argv[2]
    trip = sys.argv[3]
    stop = sys.argv[4]
else: 
    logger.info ( f'command line parameters were either missing or improperly specified. using default values...' )
    appalert ( f'command line parameters were either missing or improperly specified. using default values...' )

# Define tick size.
list = definer.ticksizes
item = [ item['tick'] for item in list if item['currency'] == pair[:3] ]
tick = Decimal( item[0] )

# Submit limit bid order.
logger.debug(f'Submitting {pair} frontrunning limit bid order.')
post = bidorder( pair, size )
post = post.json()
dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
logger.debug ( dump )

# Define poststatus class used by the "confirmexecution" function.
# Purpose: Stores the state of the orderid parameter upon exiting the websocket connection session.
class Poststatus:
    def __init__(self, state): self.__state = state
    def getvalue(self): return self.__state
    def setvalue(self, state): self.__state = state

# Define orderprice class used by the "confirmexecution" function.
# Purpose: Stores the state of the filled bid price parameter upon exiting the websocket connection session.
class Orderprice:
    def __init__(self, state): self.__state = state
    def getvalue(self): return self.__state
    def setvalue(self, state): self.__state = state

# Initialize poststatus and orderprice values used by the "confirmexecution" function.
poststatus = Poststatus('')
orderprice = Orderprice('')

# Open websocket connection.
# Determine if the bid order was filled.
confirmexecution( orderid = post['order_id'], poststatus = poststatus, orderprice = orderprice )
if 'filled' in poststatus.getvalue(): poststatus = True
if poststatus:
    executedbid = Decimal( orderprice.getvalue() )

    # Calculate trip price (skim/premium).
    tripratio = 1 + Decimal(trip)
    tripprice = Decimal( executedbid * tripratio ).quantize( tick )
    tripprice = str( tripprice )

    # Calculate stop price (i.e. the actual stop-limit price).
    stopratio = 1 + Decimal(stop)
    stopprice = Decimal( executedbid * stopratio ).quantize( tick )
    stopprice = str( stopprice )

    # Tell the user that the code is opening a websocket connection and waiting for transaction prices to increase.
    fragmentone = f'Waiting for the trading price of {pair[:3]} to increase {Decimal(trip)*100}%. '
    fragmenttwo = f'Going to stop market sell {size} {pair[:3]} when it does. Grab a snickers...'
    logger.info ( f'{fragmentone}{fragmenttwo}' )
    appalert ( f'{fragmentone}{fragmenttwo}' )

    # Open websocket connection.
    # Wait for the trading price to rise.
    # Close loop and continue executing this script when the price increase exceeds trip.
    deal = bidrise( pair, trip )

    # Submit Gemini "stop-limit" order. 
    # If in doubt about what's going on, refer to documentation here: https://docs.gemini.com/rest-api/#new-order.
    # 
    # REQUIREMENTS: The stop order limit price (i.e. "price") must be lower than the stop (i.e. "stop-limit") price.
    # RESTRICTIONS: There is no stop-market API call, so the limit price must be set very low to trigger execution.
    # DEFAULT STOP PRICE: 100 basis points above cost.
    # DEFAULT SALE PRICE: 0 basis points above cost (meaning that there is a loss when you consider API transaction fees).
    logger.debug(f'Submitting stop-limit order with a {stopprice} stop and a {executedbid} limit price to sell {size} {pair[:3]}..')
    post = limitstop( pair, size, stop, executedbid )
    post = post.json()
    dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( dump )

    # Reset poststatus and orderprice values.
    poststatus = Poststatus('')
    orderprice = Orderprice('')

    # Determine if the stopprice-limit order was filled.
    confirmexecution( orderid = post['order_id'], poststatus = poststatus, orderprice = orderprice )
    if 'filled' in poststatus.getvalue(): poststatus = True
    if poststatus:
        # cast size, gain, and cost to decimals.
        size = Decimal( size )
        cost = Decimal( executedbid )
        gain = Decimal( orderprice.getvalue() )

        # cast Gemini's api transaction fee to decimal and calculate profits.
        apifees = Decimal( definer.apitransactionfee )
        netcost = Decimal( cost * size * ( 1 + apifees ) ).quantize( tick )
        netgain = Decimal( gain * size * ( 1 - apifees ) ).quantize( tick )
        surplus = netgain - netcost

        # log profits and report them via Discord alert.
        clause0 = f'There was a profit/loss of {surplus} {pair[3:]} '
        clause1 = f'from the sale of {size} {pair[:3]} at {netgain} {pair[3:]} '
        clause2 = f'which cost {netcost} {pair[3:]} to acquire.'
        message = f'{clause0}{clause1}{clause2}'
        logger.info ( message )
        appalert ( message )

        # Let the shell know we successfully made it this far!
        sys.exit(0)
    else: sys.exit(1)
else: logger.info ( f'stop-limit order not filled.' ) ; appalert ( f'stop-limit order not filled.' )
