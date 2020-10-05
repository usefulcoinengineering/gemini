#!/usr/bin/env python3


import json

from decimal import Decimal

from libraries.logger import logger
from libraries.dealseaker import decimaldrop
from libraries.bidposter import makeliquidity
from libraries.losspreventer import limitstop
from libraries.fillvalidator import confirmexecution


# Define pair and price drop desired.
# Price depreciation defined in decimals (0.1 is 10%).
pair = 'ETHUSD'
drop = '0.000'

# Open websocket connection.
# Wait for the price to drop.
logger.info(f'waiting for {pair} to drop {Decimal(drop)*100}% in price.')
last = decimaldrop( pair, drop )
if last:

    # Set bid size.
    size = '0.001'

    # Define trigger and stop loss prices. Redefine last for submission.
    last = Decimal( last * Decimal( 0.999 ) ).quantize( Decimal('1.00') )
    trip = Decimal( last * Decimal( 0.999 ) ).quantize( Decimal('1.00') )
    stop = Decimal( trip * Decimal( 0.999 ) ).quantize( Decimal('1.00') )

    # Submit limit order.
    logger.info(f'submitting {pair} maker / post order [limit price: {last}].')
    post = makeliquidity( pair, size, str(last) )
    post = post.json()
    dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( dump )

    # Determine if the order was filled.
    fill = confirmexecution( post['order_id'] )
    logger.info(f'fill = {fill}')
    if fill:

        # Submit stop loss order.
        logger.info(f'submitting {pair} stop loss order [limit price: {stop}] triggered at {trip}.')
        post = limitstop( pair, size, str(trip), str(stop) )
        post = post.json()
        dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
        logger.debug ( dump )

    else:
        logger.debug ( "nothing to lose because the original position was not established." )
        logger.debug ( "there's nothing at risk here buddy." )
