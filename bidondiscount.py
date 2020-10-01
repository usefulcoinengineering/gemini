#!/usr/bin/env python3


import ssl
import json
import websocket
import time

from decimal import Decimal

from libraries.logger import logger as logger
from libraries.messenger import smsalert as smsalert
import libraries.authenticator as authenticator
import libraries.resourcelocator as resourcelocator

# Define session high class.
class High:
    def __init__(self, price): self.__price = price
    def getvalue(self): return self.__price
    def setvalue(self, price): self.__price = price

# Define pair.
pair = 'BTCUSD'

# Define desired price depreciation.
drop = '0.001'

# Instantiate session high object.
high = High(0)

# Define websocet functions.
def on_close(ws): logger.info(f'{ws} connection closed.')
def on_open(ws): logger.info(f'{ws} connection opened.')
def on_error(ws, error): print(error)
def on_message(ws, message, drop=drop, pair=pair, high=high):
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

                # Define bargain (deal) price.
                deal = Decimal( sessionmax * ( 1 - percentoff ) )

                # Exit loop if there's a sale.
                if deal.compare(last) == 1 :
                    logger.info( f'{pair} price [{last:.2f}] is a deal [{deal:.2f}].' )
                    smsalert( f'There was a {percentoff*100}% drop in the price of the {pair} pair on Gemini.' )
                    ws.close()

# Construct payload.
request = resourcelocator.sockgenuine + 'v1/marketdata/' + pair
nonce = int(time.time()*1000)
payload = {
    'request': request,
    'nonce': nonce
}
auth = authenticator.authenticate(payload)

# Establish websocket connection.
ws = websocket.WebSocketApp(request, on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})
