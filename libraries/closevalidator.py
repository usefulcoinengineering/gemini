#!/usr/bin/env python3
#
# library name: closevalidator.py
# library author: munair simpson
# library created: 20220817
# library purpose: continually monitor trade prices via Gemini's Websockets API until the exit threshold is breached.

import ssl
import json
import time
import datetime
import websocket

from decimal import Decimal

from libraries.logger import logger as logger
import libraries.authenticator as authenticator
from libraries.messenger import sendmessage as sendmessage

def confirmexecution(
        order: str
    ) -> None:

    # Request trade data only.
    urlrequest = "wss://api.gemini.com/v1/order/events"
    parameters = "?eventTypeFilter=closed"
    connection = urlrequest + parameters

    close_status_code = 'OK'
    close_msg = f'{connection} connection closed.'
    # Close connection arguments.
    # Reference: https://pypi.org/project/websocket-client/#:~:text=ws%2C%20close_status_code%2C%20close_msg.

    # Introduce function.
    logger.info( f'Blocking until order {order} has "closed" status on Gemini\'s orderbook...' )

    # Define websocket functions.
    def on_open( ws ) : logger.info( f'{ws} connection opened.' )
    def on_close( ws, close_status_code, close_msg ) : logger.info( 'connection closed.' )
    def on_error( ws, errormessage ) : logger.error( f'{ws} connection error: {errormessage}' )
    def on_message( ws, message, order=order ) : 
        
        # Remove comment to debug with: logger.debug( message )
        
        # Load update into a dictionary.
        dictionary = json.loads( message )

        # Check arrays for order.
        if isinstance(dictionary, list):
            for closedevent in dictionary:
                if closedevent.json()['order_id'] == order : 
                    infomessage = f'Completed the {closedevent.json()["order_type"]} {closedevent.json()["side"]}ing of '
                    infomessage = infomessage + f'{closedevent.json()["executed_amount"]} {closedevent.json()["symbol"].upper()[:3]} '
                    infomessage = infomessage + f'for {closedevent.json()["price"]:,.2f} {closedevent.json()["symbol"][3:]}. '
                    logger.info( infomessage )
                    sendmessage( infomessage )
                    ws.close()
        else: 
            # Display heartbeat
            if dictionary[ 'type' ] == "heartbeat" : logger.debug ( f'Heartbeat: {dictionary[ "socket_sequence" ]}' )

    # Construct payload.
    t = datetime.datetime.now()
    endpoint = '/v1/order/events'
    nonce = str(int(time.mktime(t.timetuple())*1000))
    payload = {
        'request': endpoint,
        'nonce': nonce
    }
    header = authenticator.authenticate(payload)
            
    # Establish websocket connection.
    # Connection is public. Public connection require neither headers nor authentication.
    logger.debug( f'Establishing websocket connection to monitor "closed" status of order {order}.' )
    ws = websocket.WebSocketApp( connection,
                                 on_open = on_open,
                                 on_close = on_close,
                                 on_error = on_error,
                                 on_message = on_message,
                                 header = header['sockheader'] )
    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})
