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

def decimaldrop(
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

    # Define websocet functions.
    def on_close(ws): logger.info(f'{ws} connection closed.')
    def on_open(ws): logger.info(f'{ws} connection opened.')
    def on_error(ws, error): logger.info(error)
    def on_message(ws, message, drop=drop, pair=pair, high=high, deal=deal):
        dictionary = json.loads( message )
        percentoff = Decimal( drop )
        sessionmax = Decimal( high.getvalue() )

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
                    logger.info( f'{move:.2f}% off highs [{sessionmax}] : {pair} is {last} presently : [Message ID: {dictionary["socket_sequence"]}].' )

                    # Define bargain (sale) price.
                    sale = Decimal( sessionmax * ( 1 - percentoff ) )

                    # Exit loop if there's a sale.
                    if sale.compare(last) == 1 :
                        logger.info( f'{pair} [now {last:.2f}] just went on sale [dropped below {sale:.2f}].' )
                        smsalert( f'There was a {percentoff*100}% drop in the price of the {pair} pair on Gemini.' )

                        # Update deal price.
                        deal.setvalue(last)
                        ws.close()

    # Construct payload.
    request = resourcelocator.sockserver + '/v1/marketdata/' + pair
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
