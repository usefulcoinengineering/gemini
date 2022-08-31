#!/usr/bin/env python3
#
# library name: marketmonitor.py
# library author: munair simpson
# library created: 20220831
# library purpose: continually monitor trade prices via Gemini's Websockets API until the exit threshold is breached.


import ssl
import json
import asyncio
import websockets

from decimal import Decimal

from libraries.logger import logger as logger
from libraries.messenger import sendmessage as sendmessage

async def blockpricerange(
        pair: str,
        upperbound: str,
        lowerbound: str
    ) -> str:
    
    # Cast as decimals.
    upperbound = Decimal( upperbound )
    lowerbound = Decimal( lowerbound )

    # Request trade data only.
    urlrequest = "wss://api.gemini.com/v1/marketdata/" + pair.lower()
    parameters = "?trades=true&heartbeat=true"
    connection = urlrequest + parameters

    # Introduce function.
    logger.info(f'Looping while {pair[:3]} prices are between {lowerbound:,.2f} {pair[3:]} and {upperbound:,.2f} {pair[3:]}')

    count = 0

    async with websockets.connect(connection) as websocket:
        while count < 1 :
            message = await websocket.recv()
            # Remove comment to debug with: logger.debug( message )
            # Load update into a dictionary.
            dictionary = json.loads( message )

            # Display heartbeat
            if dictionary[ 'type' ] == "heartbeat" : logger.debug ( f'Heartbeat: {dictionary[ "socket_sequence" ]}' )
            else :

                # Define events array/list.
                events = dictionary[ 'events' ]
                if events == [] : 
                    logger.debug( f'No update events. Received: {message}  ' )
                else:
                    # Verify the array of events is a list.
                    # Iterate through each event in the update.
                    if isinstance(events, list):
                        for event in events:
                            tradeprice = Decimal( event[ 'price' ] )
                            tradevalue = Decimal( event[ 'amount' ] )
                            amountless = Decimal( 100 * ( upperbound - tradeprice ) / upperbound )
                            amountmore = Decimal( 100 * ( tradeprice - lowerbound ) / lowerbound )
                            tradevalue = Decimal( tradevalue * tradeprice ).quantize( tradeprice )
                            if event['makerSide'] == "ask" : takeraction = "increase"
                            if event['makerSide'] == "bid" : takeraction = "decrease"
                            infomessage = f'[{amountless:.2f}% below {upperbound:,.2f} {pair[3:]} upper bound] '
                            infomessage = infomessage + f'[{amountmore:.2f}% above {lowerbound:,.2f} {pair[3:]} lower bound] '
                            infomessage = infomessage + f'{tradeprice:,.2f} {pair[3:]} price taken to '
                            infomessage = infomessage + f'quickly {takeraction} {pair[:3]} hoard by {tradevalue:,.2f} {pair[3:]}. '
                            logger.info ( f'{infomessage}' )
                            if event['makerSide'] == "ask" : 
                                if lowerbound.compare( tradeprice ) == 1 : 
                                    infomessage = f'{lowerbound:,.2f} {pair[3:]} lower/ask price bound breached. '
                                    logger.info( infomessage )
                                    sendmessage( infomessage )
                                    count = 1
                            if event['makerSide'] == "bid" : 
                                if tradeprice.compare( upperbound ) == 1 : 
                                    infomessage = f'{upperbound:,.2f} {pair[3:]} upper/bid price bound breached. '
                                    logger.info( infomessage )
                                    sendmessage( infomessage )
                                    count = 1

