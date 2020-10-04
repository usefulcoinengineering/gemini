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

def limitstop(
        pair: str,
        size: str,
        trip: str,
        stop: str
    ) -> None:

    # Construct stop loss order payload.
    # Note that sell orders require the stop_price to be greater than the price.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': size,
        'stop_price': trip,
        'price': stop,
        'side': 'sell',
        'type': 'exchange stop limit'
    }
    headers = authenticator.authenticate(payload)

    request = resourcelocator.restgenuine + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response
