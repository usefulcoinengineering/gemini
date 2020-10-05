#!/usr/bin/env python3


import requests
import ssl
import json
import websocket
import datetime
import time

from decimal import Decimal

from libraries.logger import logger as logger
from libraries.messenger import smsalert as smsalert

import libraries.authenticator as authenticator
import libraries.resourcelocator as resourcelocator

def confirmexecution(
        orderid: str
    ) -> None:

    # Introduce function.
    logger.debug(f'Confirming exection of the order identified by the Gemini assigned number: {orderid}')

    # Define websocet functions.
    def on_close(ws): logger.debug(f'{ws} connection closed.')
    def on_open(ws): logger.debug(f'{ws} connection opened.')
    def on_error(ws, error): logger.debug(error)
    def on_message(ws, message, orderid=orderid):
        dictionary = json.loads( message )
        logger.info( dictionary )

        if isinstance(dictionary, list):
            for listitem in dictionary:
                if listitem['order_id'] == orderid:
                    # Exit upon receiving order cancellation message.
                    if listitem['is_cancelled']:
                        logger.debug(f'Order {orderid} was cancelled.' ); ws.close(); return False
                    if listitem['type'] == 'cancelled':
                        logger.debug(f'Order {orderid} was cancelled [reason:{listitem["reason"]}].' ); ws.close(); return False
                    if listitem['type'] == 'rejected':
                        logger.debug(f'Order {orderid} was rejected.' ); ws.close(); return False
                    if listitem['type'] == 'fill':
                        # Make sure that the order was completely filled.
                        if listitem['remaining_amount'] == '0':
                            smsalert(f'Order {orderid} was filled.' ); ws.close(); return True

    # Construct payload.
    endpoint = '/v1/order/events'
    nonce = int(time.time()*1000)
    payload = {
        'request': endpoint,
        'nonce': nonce
    }
    header = authenticator.authenticate(payload)

    # Establish websocket connection.
    ws = websocket.WebSocketApp(str( resourcelocator.sockserver + endpoint ),
                                on_open = on_open,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close,
                                header = header['sockheader'])
    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})
