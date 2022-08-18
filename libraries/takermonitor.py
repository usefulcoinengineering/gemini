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
from libraries.messenger import sendmessage as sendmessage

def increasemonitor(
        pair: str,
        exit: str
    ) -> None:

    urlrequest = "wss://api.gemini.com/v1/marketdata/" + pair
    parameters = "?trades=true"
    connection = urlrequest + parameters

    # Introduce function.
    logger.info(f'Looping until the latest {pair[:3]} transaction price on Gemini exceeds: {exit} {pair[3:]}')

    # Define websocket functions.
    def on_open( ws ) : logger.info( f'{ws} connection opened.' )
    def on_close( ws, urlrequest, parameters ) : logger.info( f'{ws} {urlrequest + parameters} closed.' )
    def on_error( ws, errormessage ) : logger.error( f'{ws} connection error: {errormessage}' )
    def on_message( ws, message, exit=exit ) : 
        
        # Remove comment to debug with: logger.debug( message )
        
        dictionary = json.loads( message )
        events = dictionary['events']
        if events == [] : 
            logger.debug( f'no update events. perhaps this is the initial response from Gemini: {message} ' )
        else:
            # Capture the array of events to a list.
            # Iterate through each event in the update.
            if isinstance(events, list):
                for event in events:
                    tradeprice = event['price'] 
                    trade = event['amount'] 
                    if event['makerSide'] == "ask" : takeraction = "increase"
                    if event['makerSide'] == "bid" : takeraction = "decrease"
                    notification = f'{tradeprice} {pair[3:]} taken to quickly {takeraction} {pair[:3]} hoard by {trade} {pair[:3]} . '
                    logger.debug( f'{notification}' )
                    if Decimal( tradeprice ).compare( Decimal(exit) ) == 1 : 
                        notification = f'{exit} {pair[3:]} price level breached: {notification}. '
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
