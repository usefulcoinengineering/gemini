#!/usr/bin/env python3
#
# library name: takermonitor.py
# library author: munair simpson
# library created: 20220817
# library purpose: continually monitor trade prices via Gemini's Websockets API until the exit threshold is breached.


import ssl
import json
import websocket

from decimal import Decimal

from libraries.logger import logger as logger
from libraries.messenger import appalert as appalert

def increasemonitor(
        pair: str,
        exit: str
    ) -> None:

    urlrequest = "wss://api.gemini.com/v1/marketdata/" + pair
    parameters = "?trades=true"
    connection = urlrequest + parameters

    # Introduce function.
    logger.info(f'Looping until the last transaction price {pair[:3]} on Gemini exceeds: {exit} {pair[3:]}')

    # Define websocket functions.
    def on_open( ws ) : logger.info( f'{ws} connection opened.' )
    def on_close( ws ) : logger.info( f'{ws} connection closed.' )
    def on_error( ws, error ) : logger.error( error )
    def on_message( ws, message, exit=exit ) : 
        
        logger.debug( message )
        dictionary = json.loads( message )

        # Remove comment to debug with: 
        logger.debug( dictionary )
            
    # Establish websocket connection.
    # Connection is public. Public connection require neither headers nor authentication.
    logger.debug( f'Establishing websocket connection to monitor {pair[:3]} prices in {pair[3:]} terms.' )
    ws = websocket.WebSocketApp( connection,
                                 on_open = on_open,
                                 on_close = on_close,
                                 on_error = on_error,
                                 on_message = on_message )
    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})
