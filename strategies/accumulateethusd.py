#!/usr/bin/env python3


# Strategy Outline:
#  1. Accumulate ETH
#  2. Monitor price fluctuations for a 10% price drop.
#  3. Submit a limit bid order 1% below the discount price.
#  4. Place a stop loss limit ask order at 3% below the discount price.
#
# Execution:
#   - Copy this file from the strategies directory to the level below. Run with python3.

import json
import requests

from decimal import Decimal

from libraries.logger import logger
from libraries.dealseeker import pricedrop
from libraries.losspreventer import limitstop
from libraries.liquiditymaker import bidorder
from libraries.fillvalidator import confirmexecution


# Set bid size ['0.001' is the minimum for ETHUSD].
# Define pair and price drop desired.
# Price depreciation defined in decimals (0.1 is 10%).
pair = 'ETHUSD'
drop = '0.0'
size = '0.001'

# Get the latest trading price.
response = requests.get( "https://api.gemini.com/v1/pubticker/" + pair )
last = Decimal( response.json()['last'] ).quantize( Decimal('1.00') )

# Determine deal pricing.
deal = Decimal( last * ( 1 - Decimal( drop ) ) ).quantize( Decimal('1.00') )

# Calculate a competitive ask (sale) price and potential losses.
sale = Decimal( deal * Decimal( 0.99 ) ).quantize( Decimal('1.00') )
trip = Decimal( deal * Decimal( 0.98 ) ).quantize( Decimal('1.00') )
stop = Decimal( deal * Decimal( 0.97 ) ).quantize( Decimal('1.00') )
cost = Decimal( size ) * sale
loss = Decimal( size ) * stop - cost

# Explain the plan.
print (f'\n\n{pair[:3]} last sold for {last} {pair[3:]}.')
print (f'this code will wait for {pair[:3]} to drop {Decimal(drop)*100}% in price to ~{deal} {pair[3:]}.')
print (f'it will then try to buy {size} {pair[:3]} for {Decimal(cost).quantize( Decimal("1.00") )} {pair[3:]}.')
print (f'in other words it will submit a limit bid for {pair[:3]} at {sale} {pair[3:]} per {pair[:3]}.')
print (f'if the bid is successful and the order fills, it will then submit a stop loss order.')
print (f'the stop loss is not a market stop. BE CAREFUL! MAKES SURE IT IS NOT TOO CLOSE.')
print (f'it is a stop limit ask trying to sell {size} {pair[:3]} at {stop} {pair[3:]} per {pair[:3]}.')
print (f'this stop limit sale of {pair[:3]} will only trigger at {stop} {pair[3:]} per {pair[:3]}.')
print (f'if the stop loss occurs, you will lose {Decimal(loss).quantize( Decimal("1.00") )} {pair[3:]}.')
print (f'\n\n do you wish to proceed?')

verification = input(f'\tpress Y to continue...')
if verification != 'Y': exit(1)

# Open websocket connection.
# Wait for the price to drop.
logger.info(f'waiting for {pair} to drop {Decimal(drop)*100}% in price.')
deal = pricedrop( pair, drop )
if deal:

    # Define trigger and stop loss prices. Redefine deal for submission.
    sale = Decimal( deal * Decimal( 0.99 ) ).quantize( Decimal('1.00') )
    trip = Decimal( deal * Decimal( 0.98 ) ).quantize( Decimal('1.00') )
    stop = Decimal( deal * Decimal( 0.97 ) ).quantize( Decimal('1.00') )

    # Submit limit order.
    logger.info(f'submitting {pair} order [limit price: {sale}].')
    post = bidorder( pair, size, str(sale) )
    post = post.json()
    dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( dump )

    # Define poststatus class.
    # Purpose: Stores the state of the orderid parameter upon exiting the websocket connection session.
    class Poststatus:
        def __init__(self, state): self.__state = state
        def getvalue(self): return self.__state
        def setvalue(self, state): self.__state = state

    poststatus = Poststatus(False)

    # Determine if the order was filled.
    confirmexecution( orderid = post['order_id'], poststatus = poststatus )
    if poststatus.getvalue():

        # Submit stop loss order.
        logger.info(f'submitting {pair} stop loss order [limit price: {stop}] triggered at {trip}.')
        post = limitstop( pair, size, str(trip), str(stop) )
        post = post.json()
        dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
        logger.debug ( dump )

        # Determine if the order was filled.
        confirmexecution( orderid = post['order_id'], poststatus = poststatus )

    else:
        logger.debug ( "nothing to lose because the original position was not established." )
        logger.debug ( "there's nothing at risk here buddy. the post was not filled." )
