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

    # Define websocet functions.
    def on_close(ws): logger.info(f'{ws} connection closed.')
    def on_open(ws): logger.info(f'{ws} connection opened.')
    def on_error(ws, error): logger.info(error)
    def on_message(ws, message, orderid=orderid):
        dictionary = json.loads( message )

        # Process "type": "fill" messages with events only.
        if 'fill' in dictionary['type']:
            if dictionary['order_id'] == orderid:
                unfilled = dictionary['remaining_amount']

                # Make sure that the order was completely filled.
                if unfilled == 0:
                    ws.close()
                    return True

    # Construct payload.
    endpoint = '/v1/order/events'
    nonce = int(time.time()*1000)
    payload = {
        'request': endpoint,
        'nonce': nonce
    }
    header = authenticator.authenticate(payload)

    # Establish websocket connection.
    ws = websocket.WebSocketApp(str( resourcelocator.sockgenuine + endpoint ),
                                on_open = on_open,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close,
                                header = header['sockheader'])
    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})

if __name__ == "__main__":
    from fillvalidator import confirmexecution
    fill = confirmexecution( "14154213385" )
