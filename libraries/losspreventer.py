#!/usr/bin/env python3


import requests
import ssl
import json
import datetime
import time

from decimal import Decimal

from libraries.logger import logger as logger
from libraries.messenger import appalert as appalert

import libraries.definer as definer
import libraries.authenticator as authenticator

def limitstop(
        pair: str,
        size: str,
        stop: str,
        sell: str
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
        'stop_price': stop,
        'price': sell,
        'side': 'sell',
        'type': 'exchange stop limit'
    }
    headers = authenticator.authenticate(payload)

    request = definer.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])
    response = response.json()
    datadump = json.dumps( response, sort_keys=True, indent=4, separators=(',', ': ') )

    # Write the dump to logs.
    logger.debug ( datadump )
 
    try:    
        response["result"]

    # Return response.
    except KeyError as e:
        return datadump

    # Send result status and exit returning a boolean value of "True".
    appalert ( f'\"{response["reason"]}\" {response["result"]}: {response["message"]}' )
    return False