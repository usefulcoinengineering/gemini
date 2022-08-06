#!/usr/bin/env python3


import requests
import ssl
import json
import websocket
import datetime
import time

from decimal import Decimal

from libraries.logger import logger as logger
from libraries.messenger import appalert as appalert

import libraries.authenticator as authenticator
import libraries.resourcelocator as resourcelocator

def confirmexecution(
        orderid: str,
        poststatus: object,
        bidpricing: object
    ) -> None:

    # Introduce function.
    logger.debug(f'Confirming execution of the order identified by the Gemini assigned number: {orderid}')

    # Define websocket functions.
    def on_close(ws): logger.debug(f'{ws} connection closed.')
    def on_open(ws): logger.debug(f'{ws} connection opened.')
    def on_error(ws, error): logger.debug(error)
    def on_message(ws, message, orderid=orderid):
        dictionary = json.loads( message )
        exitstatus = ''

        # Remove comment to debug with: logger.debug( dictionary )

        # Check if this is an 'initial' message from Gemini.
        # It is actually the second message. The subscription acknowledgement is first.
        if dictionary == []: exitstatus = f'Order {orderid} not active.'

        if isinstance(dictionary, list):
            for listitem in dictionary:
                size = listitem['original_amount']
                pair = listitem['symbol'].upper()
                rate = listitem['price']
                side = listitem['side']
                cost = Decimal( size ) * Decimal( rate )
                bit0 = f'{pair} {side} order {orderid} valued at '
                bit1 = f'{cost.quantize( Decimal(rate) )} {pair[3:].upper()} '
                bit2 = f'[{size} {pair[:3].upper()} at {rate} {pair[3:].upper()}] was '
                text = f'{bit0}{bit1}{bit2}'
                if listitem['order_id'] == orderid:
                    # Exit upon receiving order cancellation message.
                    if listitem['is_cancelled']: exitstatus = f'{text} cancelled.'
                    if listitem['type'] == 'cancelled': exitstatus = f'{text} cancelled [reason:{listitem["reason"]}].'
                    if listitem['type'] == 'rejected': exitstatus = f'{text} rejected.'
                    if listitem['type'] == 'fill':
                        # Make sure that the order was completely filled.
                        if listitem['remaining_amount'] == '0': exitstatus = f'{text} filled.'
        if exitstatus:
            ws.close()
            logger.info ( exitstatus )
            appalert ( exitstatus )
            poststatus.setvalue( exitstatus )
            bidpricing.setvalue( rate )

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
