#!/usr/bin/env python3
#
# library name: lastmonitor.py
# library author: munair simpson
# library created: 20220816
# library purpose: monitor the latest transaction prices using Gemini's Websockets API.


# Warning:
#
# This version of lastmonitor is using synchronous communications. This may not be ideal.
# If the messages are processed faster than they are received, this code is good. If not,
# you are going to lose money.
#
# According to https://pypi.org/project/websocket_client/ [Short-lived one-off send-receive]:
# This is if you want to communicate a short message and disconnect immediately when done.


import statistics
import requests
import ssl
import json
import datetime
import time

from decimal import Decimal
from websocket import create_connection

from libraries.logger import logger as logger
from libraries.messenger import appalert as appalert

import libraries.definer as definer
import libraries.authenticator as authenticator

def pricefall(
        pair: str,
        drop: str
    ) -> None:

    # Define high class.
    # Purpose: Stores the highest trading price reached during the websocket connection session.
    class High:
        def __init__(self, price): self.__price = price
        def getvalue(self): return self.__price
        def setvalue(self, price): self.__price = price

    # Define deal class.
    # Purpose: Stores the deal (last) price reached during the websocket connection session.
    class Deal:
        def __init__(self, price): self.__price = price
        def getvalue(self): return self.__price
        def setvalue(self, price): self.__price = price

    # Instantiate high/deal objects.
    high = High(0)
    deal = Deal(0)

    # Define websocket functions.
    def on_close(ws): logger.debug(f'{ws} connection closed.')
    def on_open(ws): logger.debug(f'{ws} connection opened.')
    def on_error(ws, error): logger.debug(error)
    def on_message(ws, message, drop=drop, pair=pair, high=high, deal=deal):
        dictionary = json.loads( message )
        percentoff = Decimal( drop )
        sessionmax = Decimal( high.getvalue() )
        # Uncomment this statement to debug messages:
        logger.debug(dictionary)

        # Process "type": "update" messages with events only.
        if 'update' in dictionary['type']:
            if dictionary['events'] != []:
                events = dictionary['events']

                # Process "type": "trade" events for latest price.
                for event in events:
                    if event['type'] == 'trade' : last = Decimal( event["price"] )
                    if last.compare( Decimal(sessionmax) ) == 1 :
                        sessionmax = last
                        high.setvalue(last)

                    # Calculate movement away from high [if any].
                    move = 100 * ( sessionmax - last ) / sessionmax

                    # Display impact of event information received.
                    fragmentone = f'{move:.2f}% off of the trade event highs [i.e. {sessionmax}] monitored by the dealseaker websocket connection. '
                    fragmenttwo = f'{last} was the price of most recent {pair} trade : [Message ID: {dictionary["socket_sequence"]}].'
                    logger.info( f'{fragmentone}{fragmenttwo}' )

                    # Define bargain (sale) price.
                    sale = Decimal( sessionmax * ( 1 - percentoff ) )

                    # Exit loop if there's a sale.
                    if sale.compare(last) == 1 :
                        fragmentone = f'{pair[:3]} dropped below the {sale:.2f} target (or sale) price. It just traded at {last:.2f} {pair[3:]}. '
                        fragmenttwo = f'The highest price of {pair[:3]} since starting this websocket connection was {sessionmax:.2f}. '
                        logger.info( f'{fragmentone}{fragmenttwo}This is a {percentoff*100}% discount.' )
                        appalert( f'{fragmentone}{fragmenttwo}This is a {percentoff*100}% discount.' )

                        # Update deal price.
                        deal.setvalue(last)
                        ws.close()

    # Construct payload.
    request = definer.sockserver + '/v1/marketdata/' + pair
    nonce = int(time.time()*1000)
    payload = {
        'request': request,
        'nonce': nonce
    }
    authenticator.authenticate(payload)

    # Establish websocket connection.
    ws = websocket.WebSocketApp(request, on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})

    # Return value on discount only.
    last = Decimal( deal.getvalue() )
    if last.compare(0) == 1 :
        return last
    else: return False
