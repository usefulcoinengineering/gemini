#!/usr/bin/env python3
#
# library name: ordermanager.py
# library author: munair simpson
# library created: 20220816
# library purpose: check order number specified is active on the orderbook (i.e. has remaining size and has not been canceled).

import time
import datetime
import requests

from decimal import Decimal

from libraries.logger import logger as logger

import libraries.definer as definer
import libraries.authenticator as authenticator

def islive(
        order: str
    ) -> None:

    # Construct order status payload.
    endpoint = '/v1/order/status'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'order_id': order,
        'include_trades': False
    }
    headers = authenticator.authenticate(payload)
    request = definer.restserver + endpoint
    
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response

def cancelorder(
        order: str
    ) -> None:

    # Construct order status payload.
    endpoint = '/v1/order/cancel'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'order_id': order
    }
    headers = authenticator.authenticate(payload)
    request = definer.restserver + endpoint

    response = requests.post(request, data = None, headers = headers['restheader'])

    return response