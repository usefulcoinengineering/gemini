#!/usr/bin/env python3
#
# library name: ordermanager.py
# library author: munair simpson
# library created: 20220816
# library purpose: check order number specified is active on the orderbook (i.e. has remaining size and has not been canceled).

import sys
import ssl
import json
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
    try:
        if response.json()['is_live'] : logger.info( f'Order {order} is live on the Gemini orderbook. ' )
        else : logger.info( f'Order {order} is NOT live on the Gemini orderbook. ' )

    except KeyError as e:
        warningmessage = f'KeyError: {e} was not present in the response from the REST API server. '
        logger.warning ( f'{warningmessage} This implies that the order is no longer in the orderbook.' )
        try:    
            if response.json()["result"] : 
                logger.warning ( f'\"{response.json()["reason"]}\" {response.json()["result"]}: {response.json()["message"]}' )

        except KeyError as e:
            criticalmessage = f'KeyError: {e} was not present in the response from the REST API server.'
            logger.critical ( f'Unexpecter error. {criticalmessage}' )
            sys.exit(1)

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
    try:
        if response.json()['is_cancelled'] : logger.info( f'{order} was cancelled. ' )
        else : logger.info( f'unable to cancel {order}. ' )

    except KeyError as e:
        warningmessage = f'KeyError: {e} was not present in the response from the REST API server. '
        logger.warning ( f'{warningmessage} This implies that the order is no longer in the orderbook.' )
        try:    
            if response.json()["result"] : 
                logger.warning ( f'\"{response.json()["reason"]}\" {response.json()["result"]}: {response.json()["message"]}' )

        except KeyError as e:
            criticalmessage = f'KeyError: {e} was not present in the response from the REST API server.'
            logger.critical ( f'Unexpecter error. {criticalmessage}' )
            sys.exit(1)

    return response