#!/usr/bin/env python3
#
# script name: frontrunningtrailingstop.py
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

from distutils.log import debug
import sys
import json
import time

from decimal import Decimal

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
    notification = f'The sell price discount {sell*100}* cannot be larger than the stop price discount {stop*100}%. '
    logger.error ( f'{notification}' )
    sys.exit(1)

# Determine tick size.
item = [ item['tick'] for item in ticksizes if item['currency'] == pair[:3] ]
tick = Decimal( item[0] )

# Determine Gemini API transaction fee.
geminiapifee = Decimal( 0.0001 ) * Decimal ( notionalvolume().json()["api_maker_fee_bps"] )

# You could put the try-except logic in a while loop to keep trying until there's success.
# But keep debugging for now.
try:
    # Submit limit bid order, report response, and verify submission.
    logger.debug ( f'Submitting {pair} frontrunning limit bid order.' )
    jsonresponse = bidorder( pair, size ).json()

    # To debug remove comment character below:
    # logger.info ( json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(',', ': ') ) )
    if jsonresponse["is_cancelled"] : sys.exit(1)
    else:
        infomessage = f'Bid order {jsonresponse["order_id"]} is active and booked.'
        logger.info ( infomessage )
        sendmessage ( infomessage )

except KeyError as e:
    warningmessage = f'KeyError: {e} was not present in the response from the REST API server.'
    logger.warning ( warningmessage )
    try:    
        if jsonresponse["result"] : 
            criticalmessage = f'\"{jsonresponse["reason"]}\" {jsonresponse["result"]}: {jsonresponse["message"]}'
            logger.critical ( criticalmessage ) ; sendmessage ( criticalmessage )
            sys.exit(1)

    except KeyError as e:
        criticalmessage = f'KeyError: {e} was not present in the response from the REST API server.'
        logger.critical ( f'Unexpecter error. Unsuccessful bid order submission. {criticalmessage}' )
        sendmessage ( f'Unexpecter error. Unsuccessful bid order submission. {criticalmessage}' )
        sys.exit(1)

# Confirm order execution.
# confirmexecution( jsonresponse["order_id"] )

# Define the trade cost price and cast it.
costprice = Decimal( jsonresponse["price"] )

# Calculate exit price.
exitratio = Decimal( 1 + stop + geminiapifee )
exitprice = Decimal( costprice * exitratio ).quantize( tick )

# Calculate stop price.
stopratio = Decimal( 1 - stop )
stopprice = Decimal( costprice * stopratio ).quantize( tick )

# Calculate sell price.
sellratio = Decimal( 1 - sell - geminiapifee )
sellprice = Decimal( costprice * sellratio ).quantize( tick )

# Calculate quote gain.
quotegain = Decimal( sellprice * size - costprice * size ).quantize( tick )
ratiogain = Decimal( 100 * sellprice * size / costprice / size - 100 ).quantize( tick )

# Validate "stop price".
if stopprice.compare( costprice ) == 1:
    # Make sure that the "stop price" is below the purchase price (i.e. "cost price").
    notification = f'The stop price {stop:,.2f} {pair[3:]} cannot exceed the purchase price of {costprice:,.2f} {pair[3:]}. '
    logger.error ( f'{notification}' ) ; sendmessage ( f'{notification}' ) ; sys.exit(1)

# Record parameters to logs.
logger.debug ( f'Cost Price: {costprice}' )
logger.debug ( f'Exit Price: {exitprice}' )
logger.debug ( f'Stop Price: {stopprice}' )
logger.debug ( f'Sell Price: {sellprice}' )
logger.debug ( f'Quote Gain: {quotegain} {pair[3:]}' )
logger.debug ( f'Ratio Gain: {ratiogain:.2f}%' )

# Explain the opening a websocket connection.
# Also explain the wait for an increase in the latest transaction prices beyond the "exitprice".
notification = f'Waiting for the trading price of {pair[:3]} to rise {Decimal(stop)*100}% to {exitprice:,.2f} {pair[3:]}. '
logger.debug ( f'{notification}' ) ; sendmessage ( f'{notification}' )

# Loop.
while True :

    try: 
        # Open websocket connection. 
        bidrise( pair, exitprice ) # Wait for the trading price to rise to the exit price.
    except Exception as e:
        # Report exception.
        notification = f'The websocket connection monitoring {pair} prices probably failed. '
        logger.debug ( '{notification} Let\'s reestablish the connection and try again!' )
        continue # Restart while loop logic.
    break # Break out of the while loop because the subroutine ran successfully.

# Loop.
while True :

    time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
    
    try:
        orderstatus = islive( jsonresponse["order_id"] ).json() # Post REST API call to determine order's status.
    except Exception as e:
        logger.info ( f'Unable to retrieve order status. Error: {e}' )
        continue # Keep trying to get information on the order's status infinitely.
    try:
        if orderstatus['is_live'] : 
            logger.info( f'Bid order {orderstatus["order_id"]} is live on the Gemini orderbook. ' )
            continue # Keep retrieving information on the order's status infinitely.
        else : 
            logger.info( f'Bid order {orderstatus["order_id"]} is NOT live on the Gemini orderbook. ' )
            jsonresponse = orderstatus # Assign orderstatus to the jsonresponse used subsequently.
            break # Break out of the while loop because the subroutine ran successfully.
    except KeyError as e:
        warningmessage = f'KeyError: {e} was not present in the response from the REST API server. '
        logger.warning ( f'{warningmessage} Something went wrong.. Checking for an error message...' )
        try:    
            if orderstatus["result"] : 
                logger.warning ( f'\"{orderstatus["reason"]}\" {orderstatus["result"]}: {orderstatus["message"]}' )
                continue
        except KeyError as e:
            criticalmessage = f'KeyError: {e} was also not present in the response from the REST API server.'
            logger.critical ( f'Unexpecter error. {criticalmessage}' ) ; sendmessage ( f'Unexpecter error. {criticalmessage}' )
            continue

# Loop.
while True :

    time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
        
    # Submit initial Gemini "stop-limit" order. 
    # If in doubt about what's going on, refer to documentation here: https://docs.gemini.com/rest-api/#new-order.
    notification = f'Submitting initial stop-limit (ask) order with a {stopprice:,.2f} {pair[3:]} stop. '
    notification = notification + f'This stop limit order has a {sellprice:,.2f} {pair[3:]} limit price to sell {size} {pair[:3]}. '
    notification = notification + f'Resulting in a {ratiogain:,.2f}% gain if executed. '
    logger.debug ( f'{notification}' ) ; sendmessage ( f'{notification}' )
    try:    
        jsonresponse = askstoplimit( str(pair), str(size), str(stopprice), str(sellprice) ).json()
    except Exception as e:
        logger.info ( f'Unable to get information on ask stop limit order. Error: {e}' )
        continue # Keep trying to submit ask stop limit order.
    break # Break out of the while loop because the subroutine ran successfully.

# Loop.
while True :

    # Loop.
    while True :

        time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
        
        try:
            orderstatus = islive( jsonresponse["order_id"] ).json() # Post REST API call to determine order's status.
        except Exception as e:
            logger.info ( f'Unable to retrieve order status. Error: {e}' )
            continue # Keep trying to get information on the order's status infinitely.
        try:
            if orderstatus['is_live'] : 
                logger.info( f'Stop limit order {orderstatus["order_id"]} is live on the Gemini orderbook. ' )
                jsonresponse = orderstatus # Assign orderstatus to the jsonresponse used subsequently.
                break # Break out of the while loop because we want to reset the stop order as prices rise.
            else : 
                logger.info( f'Stop limit order {orderstatus["order_id"]} is NOT live on the Gemini orderbook. ' )
                jsonresponse = orderstatus # Assign orderstatus to the jsonresponse used subsequently.
                break # Break out of the while loop because the subroutine ran successfully.
        except KeyError as e:
            warningmessage = f'KeyError: {e} was not present in the response from the REST API server. '
            logger.warning ( f'{warningmessage} Something went wrong.. Checking for an error message...' )
            try:    
                if orderstatus["result"] : 
                    logger.warning ( f'\"{orderstatus["reason"]}\" {orderstatus["result"]}: {orderstatus["message"]}' )
                    continue
            except KeyError as e:
                criticalmessage = f'KeyError: {e} was also not present in the response from the REST API server.'
                logger.critical ( f'Unexpecter error. {criticalmessage}' ) ; sendmessage ( f'Unexpecter error. {criticalmessage}' )
                continue

    # If the stop limit order still active.
    if Decimal( jsonresponse["remaining_amount"] ).compare( Decimal(0) ) == 1 : 
        
        # Calculate new exit and resultant sell/stop prices.
        exitprice = Decimal( exitprice * exitratio ).quantize( tick )
        stopprice = Decimal( exitprice * stopratio ).quantize( tick )
        sellprice = Decimal( exitprice * sellratio ).quantize( tick )
        # Note: "costprice" is no longer used to set stop and sell prices.
        # Note: The last transaction price exceeds the previous exit price creates the new exit price.

        # Loop.
        while True :

            try: 
                # Open websocket connection. 
                bidrise( pair, exitprice ) # Wait for the trading price to rise to the exit price.
            except Exception as e:
                # Report exception.
                notification = f'The websocket connection monitoring {pair} prices probably failed. '
                logger.debug ( '{notification} Let\'s reestablish the connection and try again!' )
                continue # Restart while loop logic.
            break # Break out of the while loop because the subroutine ran successfully.


        while True :

            time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
        
            try:
                cancellationstatus = cancelorder( jsonresponse["order_id"] ).json() # Post REST API call to cancel previous order.
            except Exception as e:
                logger.info ( f'Unable to cancel order. Error: {e}' )
                continue # Keep trying to get information on the order's status infinitely.
            try:
                if cancellationstatus['is_live'] : 
                    logger.info( f'Stop limit order {cancellationstatus["order_id"]} is live on the Gemini orderbook. ' )
                    continue # Keep tring to cancel the order infinitely.
                else : 
                    logger.info( f'Stop limit order {cancellationstatus["order_id"]} is NOT live on the Gemini orderbook. ' )
                    jsonresponse = cancellationstatus # Assign orderstatus to the jsonresponse used subsequently.
                    break # Break out of the while loop because the subroutine ran successfully.
            except KeyError as e:
                warningmessage = f'KeyError: {e} was not present in the response from the REST API server. '
                logger.warning ( f'{warningmessage} Something went wrong.. Checking for an error message...' )
                try:    
                    if cancellationstatus["result"] : 
                        logger.warning ( f'\"{cancellationstatus["reason"]}\" {cancellationstatus["result"]}: {cancellationstatus["message"]}' )
                        continue
                except KeyError as e:
                    criticalmessage = f'KeyError: {e} was also not present in the response from the REST API server.'
                    logger.critical ( f'Unexpecter error. {criticalmessage}' ) ; sendmessage ( f'Unexpecter error. {criticalmessage}' )
                    continue

        while True :
            # Post updated stop-limit order.
            notification = f'Cancelled {jsonresponse["price"]:.,2f} {pair[3:]} stop sell order {jsonresponse["order_id"]}. '
            notification = f'Submitting stop-limit (ask) order with a {stopprice:,.2f} {pair[3:]} stop {sellprice:,.2f} {pair[3:]} sell.'
            logger.debug ( f'{notification}' ) ; sendmessage ( f'{notification}' )
            try:
                jsonresponse = askstoplimit( str(pair), str(size), str(stopprice), str(sellprice) ).json()
            except Exception as e:
                logger.info ( f'Unable to get information on {jsonresponse["remaining_amount"]}. Error: {e}' )
                time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
                continue # Keep trying to post stop limit order infinitely.
            break # Break out of the while loop because the subroutine ran successfully.
        continue

    else :

        # Recalculate quote gain.
        quotegain = Decimal( sellprice * size - costprice * size ).quantize( tick )
        ratiogain = Decimal( 100 * sellprice * size / costprice / size - 100 )

        # log profits and report them via Discord alert.
        clause0 = f'There was a {ratiogain:,.2f}% profit/loss of {quotegain:,.2f} {pair[3:]} '
        clause1 = f'from the sale of {size} {pair[:3]} at {Decimal(sellprice * size):,.2f} {pair[3:]} '
        clause2 = f'which cost {Decimal(costprice * size):,.2f} {pair[3:]} to acquire.'
        message = f'{clause0}{clause1}{clause2}'
        logger.info ( message ) ; sendmessage ( message )
        break

# Let the shell know we successfully made it this far!
sys.exit(0)
