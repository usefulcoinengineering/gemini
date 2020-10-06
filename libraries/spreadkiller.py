#!/usr/bin/env python3


import requests
import ssl
import json
import datetime
import time

from decimal import Decimal

from libraries.logger import logger as logger

import libraries.authenticator as authenticator
import libraries.resourcelocator as resourcelocator

def biding(
        pair: str,
        size: str,
    ) -> None:

    # Get the lowest ask in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( resourcelocator.restserver + endpoint )
    market = Decimal( response.json()['ask'] )
    zeros = str( Decimal( 0 ).quantize( market ) )
    tick = Decimal( zeros[:1] + '1' )
    bid = market - tick

    logger.debug(f'endpoint: {endpoint}'')
    logger.debug(f'market: {market}'')
    logger.debug(f'zeros: {zeros}'')
    logger.debug(f'tick: {tick}'')
    logger.debug(f'bid: {bid}'')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': size,
        'price': bid,
        'side': 'buy',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = resourcelocator.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response
