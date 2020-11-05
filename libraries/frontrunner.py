#!/usr/bin/env python3
#
# library name: frontrunner.py
# library author: munair simpson
# library created: 20201029
# library purpose: bid/ask one tick above/below the best bid/ask offer.


import requests
import ssl
import json
import datetime
import time

from decimal import Decimal

from libraries.logger import logger as logger

import libraries.constants as constants
import libraries.authenticator as authenticator
import libraries.resourcelocator as resourcelocator

def bidorder(
        pair: str,
        size: str,
    ) -> None:

    # Determine tick size.
    list = constants.ticksizes
    item = [ item['tick'] for item in list if item['currency'] == pair[:3] ]
    tick = Decimal( item[0] )

    # Get the highest bid in the orderbook.
    # Make an offer that's one tick better.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( resourcelocator.restserver + endpoint )
    bidprice = Decimal( response.json()['bid'] )
    offering = str( Decimal( bidprice + tick ).quantize( tick ) )
    quantity = str( Decimal( size ).quantize( tick ) )

    # Update logs.
    logger.debug(f'bidprice: {bidprice}')
    logger.debug(f'offering: {offering}')
    logger.debug(f'quantity: {quantity}')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': quantity,
        'price': offering,
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
    fraction = Decimal( constants.apitransactionfee )
    notional = Decimal(cash) / Decimal( 1 + fraction )

    # Determine tick size.
    list = constants.ticksizes
    item = [ item['tick'] for item in list if item['currency'] == pair[:3] ]
    tick = Decimal( item[0] )

    # Get the highest bid in the orderbook.
    # Make an offer that's one tick better.
    # Then determine the bid order size.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( resourcelocator.restserver + endpoint )
    bidprice = Decimal( response.json()['bid'] )
    offering = str( Decimal( bidprice + tick ).quantize( tick ) )
    quantity = str( Decimal( notional / Decimal(offering) ).quantize( tick ) )

    # Update logs.
    logger.debug(f'bidprice: {bidprice}')
    logger.debug(f'offering: {offering}')
    logger.debug(f'quantity: {quantity}')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': quantity,
        'price': offering,
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

    # Determine tick size.
    list = constants.ticksizes
    item = [ item['tick'] for item in list if item['currency'] == pair[:3] ]
    tick = Decimal( item[0] )

    # Get the lowest ask in the orderbook.
    # Make an offer that's one tick better.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( resourcelocator.restserver + endpoint )
    askprice = Decimal( response.json()['ask'] )
    offering = str( Decimal( askprice - tick ).quantize( tick ) )
    quantity = str( Decimal( size ).quantize( tick ) )

    # Update logs.
    logger.debug(f'askprice: {askprice}')
    logger.debug(f'offering: {offering}')
    logger.debug(f'quantity: {quantity}')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': quantity,
        'price': offering,
        'side': 'sell',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = resourcelocator.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response

def quotaask(
        pair: str,
        cash: str,
    ) -> None:

    # Determine API transaction fee.
    # Refer to https://docs.gemini.com/rest-api/#basis-point.
    # Fees are calculated on the notional value of each trade (price × size).
    # Meaning (for API transactions): size * price * 1.001 = cash
    fraction = Decimal( constants.apitransactionfee )
    notional = Decimal(cash) / Decimal( 1 + fraction )

    # Determine tick size.
    list = constants.ticksizes
    item = [ item['tick'] for item in list if item['currency'] == pair[:3] ]
    tick = Decimal( item[0] )

    # Get the lowest ask in the orderbook.
    # Make an offer that's one tick better.
    # Then determine the ask order size.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( resourcelocator.restserver + endpoint )
    askprice = Decimal( response.json()['ask'] )
    offering = str( Decimal( askprice - tick ).quantize( tick ) )
    quantity = str( Decimal( notional / Decimal(offering) ).quantize( tick ) )

    # Update logs.
    logger.debug(f'askprice: {askprice}')
    logger.debug(f'offering: {offering}')
    logger.debug(f'quantity: {quantity}')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': quantity,
        'price': offering,
        'side': 'sell',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = resourcelocator.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response
