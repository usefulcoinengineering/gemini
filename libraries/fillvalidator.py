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
        orderid: str,
        poststatus: object
    ) -> None:

    # Introduce function.
    logger.debug(f'Confirming execution of the order identified by the Gemini assigned number: {orderid}')

    # Define websocet functions.
    def on_close(ws): logger.debug(f'{ws} connection closed.')
    def on_open(ws): logger.debug(f'{ws} connection opened.')
    def on_error(ws, error): logger.debug(error)
    def on_message(ws, message, orderid=orderid):
        dictionary = json.loads( message )
        # Remove comment to debug with: logger.debug( dictionary )

        # Remove comment to log heartbeat: if dictionary['type'] == 'heartbeat': logger.debug( dictionary )

        # Process "type": "heartbeat" messages.
        logger.debug( dictionary )
            # beatback = { 'type': 'pong' }
            # ws.send( json.dumps(beatback) )
            # logger.debug( beatback.json() )

        exitstatus = False
        if isinstance(dictionary, list):

            # Check if this is an 'initial' message from Gemini.
            if any(listitem['type'] == 'initial' for listitem in dictionary):
                if not any(listitem['order_id'] == orderid for listitem in dictionary):
                    jsonoutput = json.dumps( dictionary, sort_keys=True, indent=4, separators=(',', ': ') )
                    exitstatus = f'Order not active - \n{jsonoutput}'

            else:
                for listitem in dictionary:
                    size = listitem['original_amount']
                    rate = listitem['price']
                    deal = f'Order {orderid} for {size} at {rate} was '
                    if listitem['order_id'] == orderid:
                        # Exit upon receiving order cancellation message.
                        if listitem['is_cancelled']: exitstatus = f'{deal} cancelled.'
                        if listitem['type'] == 'cancelled': exitstatus = f'{deal} cancelled [reason:{listitem["reason"]}].'
                        if listitem['type'] == 'rejected': exitstatus = f'{deal} was rejected.'
                        if listitem['type'] == 'fill':
                            # Make sure that the order was completely filled.
                            if listitem['remaining_amount'] == '0': exitstatus = f'{deal} was filled.'
        if exitstatus:
            ws.close()
            logger.info ( exitstatus )
            smsalert ( exitstatus )
            poststatus.setvalue( True )

    # Construct payload.
    endpoint = '/v1/order/events'
    nonce = int(time.time()*1000)
    payload = {
        'request': endpoint,
        'nonce': nonce
    }
    header = authenticator.authenticate(payload)

    # Establish websocket connection.
    logger.debug( f'Establishing websocket connection to confirm the execution of order number {orderid}.' )
    ws = websocket.WebSocketApp(str( resourcelocator.sockserver + endpoint ),
                                on_open = on_open,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close,
                                header = header['sockheader'])
    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})
