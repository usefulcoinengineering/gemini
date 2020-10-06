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

def bidorder(
        pair: str,
        size: str,
    ) -> None:

    # Get the lowest ask in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( resourcelocator.restserver + endpoint )
    market = Decimal( response.json()['ask'] )
    zeros = str( Decimal( 0 ).quantize( market ) )
    tick = Decimal( zeros  + '1' ) * 10
    bid = str( market - Decimal( tick ).quantize( market ) )

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

def quotabid(
        pair: str,
        cash: str,
    ) -> None:

    # Determine API transaction fee.
    # Refer to https://docs.gemini.com/rest-api/#basis-point.
    # Fees are calculated on the notional value of each trade (price × size).
    # Meaning (for API transactions): size * price * 1.001 = cash
    fraction = 0.001
    notional = Decimal(cash) / Decimal( 1 + fraction )

    # Get the lowest ask in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( resourcelocator.restserver + endpoint )
    market = Decimal( response.json()['ask'] )
    zeros = str( Decimal( 0 ).quantize( market ) )
    tick = Decimal( zeros  + '1' ) * 10
    bid = str( market - Decimal( tick ).quantize( market ) )

    # Determin bid size.
    quantity = notional / Decimal(bid)
    size = str( quantity.quantize( Decimal('1.00') ) )

    logger.debug(f'quantity: {quantity}')
    logger.debug(f'size: {size}')

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

def askorder(
        pair: str,
        size: str,
    ) -> None:

    # Get the lowest ask in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( resourcelocator.restserver + endpoint )
    market = Decimal( response.json()['bid'] )
    zeros = str( Decimal( 0 ).quantize( market ) )
    tick = Decimal( zeros  + '1' ) * 10
    ask = str( market + Decimal( tick ).quantize( market ) )

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': size,
        'price': ask,
        'side': 'sell',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = resourcelocator.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response
