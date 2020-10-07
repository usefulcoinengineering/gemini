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
        last: str
    ) -> None:

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': size,
        'price': str(last),
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
        last: str
    ) -> None:

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': size,
        'price': str(last),
        'side': 'sell',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = resourcelocator.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response
