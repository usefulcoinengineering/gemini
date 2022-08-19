#!/usr/bin/env python3
#
# library name: closevalidator.py
# library author: munair simpson
# library created: 20220817
# library purpose: continually monitor trade prices via Gemini's Websockets API until the exit threshold is breached.

import ssl
import json
import websocket

from decimal import Decimal

from libraries.logger import logger as logger
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
        closedevents = json.loads( message )

        # Verify the array of events is a list.
        # Iterate through each event in the update.
        if isinstance(closedevents, list):
            for closedevent in closedevents:
                closedorder = Decimal( closedevent['order_id'] )
                if closedorder == order : 
                    notification = f'Completed the {closedevent["order_type"]} {closedevent["side"]}ing of '
                    notification = notification + f'{closedevent["executed_amount"]} {closedevent["executed_amount"][:3]} '
                    notification = notification + f'for {closedevent["price"]:,.2f} {closedevent["executed_amount"][3:]}. '
                    logger.info( notification )
                    sendmessage( notification )
                    ws.close()
            
    # Establish websocket connection.
    # Connection is public. Public connection require neither headers nor authentication.
    logger.debug( f'Establishing websocket connection to monitor {pair[:3]} prices in {pair[3:]} terms.' )
    ws = websocket.WebSocketApp( connection,
                                 on_open = on_open,
                                 on_close = on_close,
                                 on_error = on_error,
                                 on_message = on_message )
    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})
