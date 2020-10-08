#!/usr/bin/env python3


# Strategy Outline:
#  1. Urgently need ETH but waiting to realize the Gemini transactin fee.
#  2. Monitor price fluctuations for a 20 basis point price drop.
#  3. Submit a limit bid order 20 basis points below the discount price.
#
# Execution:
#   - Copy this file from the strategies directory to the level below. Run with python3.

import json
import requests

from decimal import Decimal

from libraries.logger import logger
from libraries.dealseaker import pricedrop
from libraries.liquiditymaker import bidorder
from libraries.liquiditymaker import askorder
from libraries.fillvalidator import confirmexecution


# Set bid size ['0.001' is the minimum for ETHUSD].
# Define pair and price drop desired (at least 2X fees).
# Price depreciation defined in decimals (0.1 is 10%).
pair = 'ETHUSD'
drop = '0.002'
size = '1.000'

# Get the latest trading price.
response = requests.get( "https://api.gemini.com/v1/pubticker/" + pair )
last = Decimal( response.json()['last'] ).quantize( Decimal('1.00') )

# Determine deal pricing.
deal = Decimal( last * ( 1 - Decimal( drop ) ) ).quantize( Decimal('1.00') )

# Calculate a competitive ask (sale) price and potential losses.
sale = Decimal( deal * ( 1 - Decimal( drop ) ) ).quantize( Decimal('1.00') )
fees = Decimal( deal * ( 1 + Decimal( drop ) ) ).quantize( Decimal('1.00') )
cost = Decimal( size ) * sale
gain = Decimal( size ) * fees - cost

# Explain the plan.
print (f'\n\n{pair[:3]} last sold for {last} {pair[3:]}.')
print (f'this code will wait for {pair[:3]} to drop {Decimal(drop)*100}% in price to ~{deal} {pair[3:]}.')
print (f'it will then try to buy {size} {pair[:3]} for {Decimal(cost).quantize( Decimal("1.00") )} {pair[3:]}.')
print (f'in other word it will submit a limit bid for {pair[:3]} at {sale} {pair[3:]} per {pair[:3]}.')
print (f'if the bid is successful and the order fills, it will then submit a limit ask order.')
print (f'BE CAREFUL! YOU COULD LOSE THE TOTAL VALUE OF THE ORDER IF THE PRICE NEVER BOUNCES BACK UP.')
print (f'the limit ask order is trying to sell {size} {pair[:3]} at {fees} {pair[3:]} per {pair[:3]}.')
print (f'if the limit ask is successful, you will be able to acquire {size} for free on Gemini.')
print (f'that is because you will have locked in a realized gain of {Decimal(gain).quantize( Decimal("1.00") )} {pair[3:]}.')
print (f'\n\n do you wish to proceed?')

verification = input(f'\tpress Y to continue...')
if verification != 'Y': exit(1)

# Open websocket connection.
# Wait for the price to drop.
logger.info(f'waiting for {pair} to drop {Decimal(drop)*100}% in price.')
deal = pricedrop( pair, drop )
if deal:

    # Define trigger and stop loss prices. Redefine deal for submission.
    sale = Decimal( deal * ( 1 - Decimal( drop ) ) ).quantize( Decimal('1.00') )
    fees = Decimal( deal * ( 1 + Decimal( drop ) ) ).quantize( Decimal('1.00') )

    # Submit limit bid order.
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

        # Submit limit ask order.
        logger.info(f'submitting {pair} limit ask order [limit price: {fees}].')
        post = askorder( pair, size, str(fees) )
        post = post.json()
        dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
        logger.debug ( dump )

        # Determine if the order was filled.
        confirmexecution( orderid = post['order_id'], poststatus = poststatus )

        # Calculate gain/loss.
        cost = Decimal( size ) * sale
        gain = Decimal( size ) * fees - cost
        logger.debug ( f'absolute gain: {gain} {pair[3:]}' )
        logger.debug ( f'relative gain: {gain}: {Decimal(gain/cost).quantize( Decimal("1.00") )}%' )

    else:
        logger.debug ( 'ask not submitted because the bid was not filled.' )
