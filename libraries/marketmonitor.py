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

def pricedecrease(
        pair: str,
        exit: str
    ) -> None:

    # Cast as decimal.
    exit = Decimal( exit )

    # Request trade data only.
    urlrequest = "wss://api.gemini.com/v1/marketdata/" + pair.lower()
    parameters = "?trades=true&heartbeat=true"
    connection = urlrequest + parameters

    close_status_code = 'OK'
    close_msg = f'{connection} connection closed.'
    # Close connection arguments.
    # Reference: https://pypi.org/project/websocket-client/#:~:text=ws%2C%20close_status_code%2C%20close_msg.


    # Introduce function.
    logger.info(f'Looping until the latest {pair[:3]} transaction price on Gemini drops below: {exit:,.2f} {pair[3:]}')

    # Define websocket functions.
    def on_open( ws ) : logger.info( f'{ws} connection opened.' )
    def on_close( ws, close_status_code, close_msg ) : logger.info( 'connection closed.' )
    def on_error( ws, errormessage ) : logger.error( f'{ws} connection error: {errormessage}' )
    def on_message( ws, message, pair=pair.upper(), exit=exit ) : 
        
        # Display heartbeat
        if message.json()["type"] == "heartbeat" : 
            logger.debug ( f'heartbeat: {message.json()["sequence"]}' )
            continue
        # Remove comment to debug with: logger.debug( message )
        
        # Load update into a dictionary.
        dictionary = json.loads( message )

        # Define events array/list.
        events = dictionary['events']
        if events == [] : 
            logger.debug( f'no update events. perhaps this is the initial response from Gemini: {message} ' )
        else:
            # Verify the array of events is a list.
            # Iterate through each event in the update.
            if isinstance(events, list):
                for event in events:
                    tradeprice = Decimal( event['price'] )
                    tradevalue = Decimal( event['amount'] )
                    inadequacy = Decimal( 100 * ( tradeprice - exit ) / exit )
                    tradevalue = Decimal( tradevalue * tradeprice ).quantize( tradeprice )
                    if event['makerSide'] == "ask" : takeraction = "increase"
                    if event['makerSide'] == "bid" : takeraction = "decrease"
                    notification = f'[{inadequacy:.2f}% off {exit:,.2f} {pair[3:]}] {tradeprice} {pair[3:]} price taken to '
                    notification = notification + f'quickly {takeraction} {pair[:3]} hoard by {tradevalue:,.2f} {pair[3:]}. '
                    logger.debug( f'{notification}' )
                    if exit.compare( tradeprice ) == 1 : 
                        notification = f'{exit:,.2f} {pair[3:]} price level breached: {notification}'
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

def askfall(
        pair: str,
        exit: str
    ) -> None:

    # Cast as decimal.
    exit = Decimal( exit )

    # Request trade data only.
    urlrequest = "wss://api.gemini.com/v1/marketdata/" + pair.lower()
    parameters = "?trades=true&heartbeat=true"
    connection = urlrequest + parameters

    close_status_code = 'OK'
    close_msg = f'{connection} connection closed.'
    # Close connection arguments.
    # Reference: https://pypi.org/project/websocket-client/#:~:text=ws%2C%20close_status_code%2C%20close_msg.


    # Introduce function.
    logger.info(f'Looping until the latest {pair[:3]} transaction price on Gemini drops below: {exit:,.2f} {pair[3:]}')

    # Define websocket functions.
    def on_open( ws ) : logger.info( f'{ws} connection opened.' )
    def on_close( ws, close_status_code, close_msg ) : logger.info( 'connection closed.' )
    def on_error( ws, errormessage ) : logger.error( f'{ws} connection error: {errormessage}' )
    def on_message( ws, message, pair=pair.upper(), exit=exit ) : 
        
        # Display heartbeat
        if message.json()["type"] == "heartbeat" : 
            logger.debug ( f'heartbeat: {message.json()["sequence"]}' )
            continue
        # Remove comment to debug with: logger.debug( message )
        
        # Load update into a dictionary.
        dictionary = json.loads( message )

        # Define events array/list.
        events = dictionary['events']
        if events == [] : 
            logger.debug( f'no update events. perhaps this is the initial response from Gemini: {message} ' )
        else:
            # Verify the array of events is a list.
            # Iterate through each event in the update.
            if isinstance(events, list):
                for event in events:
                    tradeprice = Decimal( event['price'] )
                    tradevalue = Decimal( event['amount'] )
                    inadequacy = Decimal( 100 * ( tradeprice - exit ) / exit )
                    tradevalue = Decimal( tradevalue * tradeprice ).quantize( tradeprice )
                    if event['makerSide'] == "ask" : takeraction = "increase"
                    if event['makerSide'] == "bid" : takeraction = "decrease"
                    notification = f'[{inadequacy:.2f}% off {exit:,.2f} {pair[3:]}] {tradeprice} {pair[3:]} price taken to '
                    notification = notification + f'quickly {takeraction} {pair[:3]} hoard by {tradevalue:,.2f} {pair[3:]}. '
                    logger.debug( f'{notification}' )
                    if event['makerSide'] == "ask" :
                        if exit.compare( tradeprice ) == 1 : 
                            notification = f'{exit:,.2f} {pair[3:]} price level breached: {notification}'
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

def priceincrease(
        pair: str,
        exit: str
    ) -> None:

    # Cast as decimal.
    exit = Decimal( exit )
    
    # Request trade data only.
    urlrequest = "wss://api.gemini.com/v1/marketdata/" + pair.lower()
    parameters = "?trades=true&heartbeat=true"
    connection = urlrequest + parameters

    close_status_code = 'OK'
    close_msg = f'{connection} connection closed.'
    # Close connection arguments.
    # Reference: https://pypi.org/project/websocket-client/#:~:text=ws%2C%20close_status_code%2C%20close_msg.


    # Introduce function.
    logger.info(f'Looping until the latest {pair[:3]} transaction price on Gemini exceeds: {exit:,.2f} {pair[3:]}')

    # Define websocket functions.
    def on_open( ws ) : logger.info( f'{ws} connection opened.' )
    def on_close( ws, close_status_code, close_msg ) : logger.info( 'connection closed.' )
    def on_error( ws, errormessage ) : logger.error( f'{ws} connection error: {errormessage}' )
    def on_message( ws, message, pair=pair.upper(), exit=exit ) : 
        
        # Display heartbeat
        if message.json()["type"] == "heartbeat" : 
            logger.debug ( f'heartbeat: {message.json()["sequence"]}' )
            continue
        # Remove comment to debug with: logger.debug( message )
        
        # Load update into a dictionary.
        dictionary = json.loads( message )

        # Define events array/list.
        events = dictionary['events']
        if events == [] : 
            logger.debug( f'no update events. perhaps this is the initial response from Gemini: {message} ' )
        else:
            # Verify the array of events is a list.
            # Iterate through each event in the update.
            if isinstance(events, list):
                for event in events:
                    tradeprice = Decimal( event['price'] )
                    tradevalue = Decimal( event['amount'] )
                    inadequacy = Decimal( 100 * ( exit - tradeprice ) / exit )
                    tradevalue = Decimal( tradevalue * tradeprice ).quantize( tradeprice )
                    if event['makerSide'] == "ask" : takeraction = "increase"
                    if event['makerSide'] == "bid" : takeraction = "decrease"
                    notification = f'[{inadequacy:.2f}% off {exit:,.2f} {pair[3:]}] {tradeprice} {pair[3:]} price taken to '
                    notification = notification + f'quickly {takeraction} {pair[:3]} hoard by {tradevalue:,.2f} {pair[3:]}. '
                    logger.debug( f'{notification}' )
                    if tradeprice.compare( exit ) == 1 : 
                        notification = f'{exit:,.2f} {pair[3:]} price level breached: {notification}'
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

def bidrise(
        pair: str,
        exit: str
    ) -> None:

    # Cast as decimal.
    exit = Decimal( exit )

    # Request trade data only.
    urlrequest = "wss://api.gemini.com/v1/marketdata/" + pair.lower()
    parameters = "?trades=true&heartbeat=true"
    connection = urlrequest + parameters

    close_status_code = 'OK'
    close_msg = f'{connection} connection closed.'
    # Close connection arguments.
    # Reference: https://pypi.org/project/websocket-client/#:~:text=ws%2C%20close_status_code%2C%20close_msg.


    # Introduce function.
    logger.info(f'Looping until the latest {pair[:3]} transaction price on Gemini exceeds: {exit:,.2f} {pair[3:]}')

    # Define websocket functions.
    def on_open( ws ) : logger.info( f'{ws} connection opened.' )
    def on_close( ws, close_status_code, close_msg ) : logger.info( 'connection closed.' )
    def on_error( ws, errormessage ) : logger.error( f'{ws} connection error: {errormessage}' )
    def on_message( ws, message, pair=pair.upper(), exit=exit ) : 
        
        # Display heartbeat
        if message.json()["type"] == "heartbeat" : 
            logger.debug ( f'heartbeat: {message.json()["sequence"]}' )
            continue
        # Remove comment to debug with: logger.debug( message )
        
        # Load update into a dictionary.
        dictionary = json.loads( message )

        # Define events array/list.
        events = dictionary['events']
        if events == [] : 
            logger.debug( f'no update events. perhaps this is the initial response from Gemini: {message} ' )
        else:
            # Verify the array of events is a list.
            # Iterate through each event in the update.
            if isinstance(events, list):
                for event in events:
                    tradeprice = Decimal( event['price'] )
                    tradevalue = Decimal( event['amount'] )
                    inadequacy = Decimal( 100 * ( exit - tradeprice ) / exit )
                    tradevalue = Decimal( tradevalue * tradeprice ).quantize( tradeprice )
                    if event['makerSide'] == "ask" : takeraction = "increase"
                    if event['makerSide'] == "bid" : takeraction = "decrease"
                    notification = f'[{inadequacy:.2f}% off {exit:,.2f} {pair[3:]}] {tradeprice} {pair[3:]} price taken to '
                    notification = notification + f'quickly {takeraction} {pair[:3]} hoard by {tradevalue:,.2f} {pair[3:]}. '
                    logger.debug( f'{notification}' )
                    if event['makerSide'] == "bid" : 
                        if tradeprice.compare( exit ) == 1 : 
                            notification = f'{exit:,.2f} {pair[3:]} price level breached: {notification}'
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

