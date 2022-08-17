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

from mmap import ACCESS_DEFAULT
import sys
import json
import requests

from decimal import Decimal

import libraries.definer as definer

from libraries.logger import logger
from libraries.bidmonitor import anchoredrise
from libraries.orderchecker import islive
from libraries.frontrunner import bidorder
from libraries.losspreventer import limitstop
from libraries.skimvalidator import confirmexecution
from libraries.messenger import appalert as appalert
from libraries.definer import ticksizes as ticksizes

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
    logger.debug ( f'incorrect number of command line arguments. using default values for {pair} trailing...' )

# Make sure "sell" is more than "stop".
# Gemini requires this for stop ask orders:
# The stop price must exceed the sell price.
if Decimal(sell).compare( Decimal(stop) ) == 1:
    notice = f'The sale price {sell} {pair[3:]} cannot be larger than the stop price {stop} {pair[3:]}. '
    logger.debug ( f'{notice}' )
    sys.exit(1)

# Determine Gemini API transaction fee.
apifee = Decimal( definer.apitransactionfee )

# Determine tick size.
item = [ item['tick'] for item in ticksizes if item['currency'] == pair[:3] ]
tick = Decimal( item[0] )

# Submit limit bid order and dump the JSON response in the logs.
logger.debug ( f'Submitting {pair} frontrunning limit bid order.' )
postresponse = bidorder( pair, size )
jsonresponse = postresponse.json()
jsondatadump = json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(',', ': ') )
logger.debug ( jsondatadump )

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
confirmexecution( orderid = jsonresponse['order_id'], poststatus = poststatus, orderprice = orderprice )
if 'filled' in poststatus.getvalue(): poststatus = True
if poststatus:
    costprice = Decimal( orderprice.getvalue() )

    # Calculate exit price.
    exitratio = Decimal( 1 + stop + apifee )
    exitprice = Decimal( costprice * exitratio ).quantize( tick )
    exitprice = str( exitprice )
    
    # Calculate stop price.
    stopratio = Decimal( 1 - stop )
    stopprice = Decimal( costprice * stopratio ).quantize( tick )
    stopprice = str( stopprice )

    # Calculate sell price.
    sellratio = Decimal( 1 - sell - apifee )
    sellprice = Decimal( costprice * sellratio ).quantize( tick )
    sellprice = str( sellprice )

    # Calculate quote gain.
    quotegain = Decimal( sellprice * size - costprice * size ).quantize( tick )
    ratiogain = Decimal( 100 * sellprice * size / costprice * size - 100 )
    quotegain = str( quotegain )
    ratiogain = str( f'{ratiogain}%' )

    # Validate "stop price".
    if stopprice.compare( costprice ) == 1:
        # Make sure that the "stop price" is below the purchase price (i.e. "cost price").
        notice = f'The stop price {stop} {pair[3:]} cannot be larger than the purchase price of {costprice} {pair[3:]}. '
        logger.debug ( f'{notice}' ) ; appalert ( f'{notice}' ) ; sys.exit(1)

    # Record parameters to logs.
    logger.debug ( f'cost price: {costprice}' )
    logger.debug ( f'exit price: {exitprice}' )
    logger.debug ( f'stop price: {stopprice}' )
    logger.debug ( f'sell price: {sellprice}' )
    logger.debug ( f'quote gain: {quotegain}' )
    logger.debug ( f'ratio gain: {ratiogain}' )

    # Tell the user that the code is opening a websocket connection and waiting for transaction prices to increase.
    fragmentone = f'Waiting for the trading price of {pair[:3]} to increase {Decimal(stop)*100}% to {exitprice} {pair[3:]}. '
    fragmenttwo = f'Going to submit a stop limit sell {size} {pair[:3]} at {stopprice} {pair[3:]} when it does. '
    logger.info ( f'{fragmentone}{fragmenttwo}' ) ; appalert ( f'{fragmentone}{fragmenttwo}' )

    # Open websocket connection.
    # Wait for the trading price to rise to the exit price.
    # Close loop and continue executing this script when the price increase exceeds trip.
    exitprice = anchoredrise( pair, exitprice )

    # Submit Gemini "stop-limit" order. 
    # If in doubt about what's going on, refer to documentation here: https://docs.gemini.com/rest-api/#new-order.
    alertmessage = f'Submitting stop-limit (ask) order with a {stopprice} {pair[3:]} stop. '
    alertmessage = alertmessage + f'This stop limit order a {sellprice} {pair[3:]} limit price to sell {size} {pair[:3]}. '
    alertmessage = alertmessage + f'Resulting in a {ratiogain} if executed. '
    logger.debug ( f'{alertmessage}' )
    postresponse = limitstop( pair, size, stop, sell )
    jsonresponse = postresponse.json()
    jsondatadump = json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( jsondatadump )

    # Loop until sold.
    # Using the REST API to determine if the order was filled.
    while islive :

        # Update exitprice.
        # Use it set stop and sell prices.
        exitprice = anchoredrise( pair, exitprice )
        stopprice = Decimal( exitprice * stopratio )
        sellprice = Decimal( exitprice * sellratio )
        # Note: "costprice" is no longer used to set stop and sell prices.
        # Note: The last transaction prices exceeds the previous exit price creates the new exit price.

        # Update stop-limit order.
        appalert ( "Should be updating stop order now, but the code isn't written." )

    # Recalculate quote gain.
    quotegain = Decimal( sellprice * size - costprice * size ).quantize( tick )
    ratiogain = Decimal( 100 * sellprice * size / costprice * size - 100 )
    quotegain = str( quotegain )
    ratiogain = str( f'{ratiogain}%' )

    # log profits and report them via Discord alert.
    clause0 = f'There was a {ratiogain} profit/loss of {quotegain} {pair[3:]} '
    clause1 = f'from the sale of {size} {pair[:3]} at {Decimal(sellprice * size)} {pair[3:]} '
    clause2 = f'which cost {Decimal(costprice * size)} {pair[3:]} to acquire.'
    message = f'{clause0}{clause1}{clause2}'
    logger.info ( message ) ; appalert ( message )

    # Let the shell know we successfully made it this far!
    sys.exit(0)

else: logger.info ( f'bid order not filled.' ) ; appalert ( f'bid order not filled.' )
