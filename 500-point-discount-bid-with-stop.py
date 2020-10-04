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
drop = '0.0001'

# Open websocket connection.
# Wait for the price to drop.
last = decimaldrop( pair, drop )
if last:

    # Set bid size.
    size = '0.01'

    # Define trigger and stop loss prices. Redefine last for submission.
    last = Decimal( last * Decimal( 0.999 ) ).quantize( Decimal('1.00') )
    trip = Decimal( last * Decimal( 0.999 ) ).quantize( Decimal('1.00') )
    stop = Decimal( trip * Decimal( 0.999 ) ).quantize( Decimal('1.00') )

    post = makeliquidity( pair, size, str(last) )
    post = post.json()
    dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.info ( dump )

    # Determine if the order was filled.
    load = json.loads( dump )
    swap = load['order_id']
    fill = confirmexecution( swap )
    if fill:

        # Submit stop loss order.
        post = limitstop( pair, size, str(trip), str(stop) )
        post = post.json()
        dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
        logger.info ( dump )
