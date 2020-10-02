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

# Define purchase quantity.
size = '0.0001'

# Define pair.
pair = 'BTCUSD'

# Define desired price depreciation.
drop = '0.001'

# Instantiate high/deal objects.
high = High(0)
deal = Deal(0)

# Define websocet functions.
def on_close(ws): logger.info(f'{ws} connection closed.')
def on_open(ws): logger.info(f'{ws} connection opened.')
def on_error(ws, error): print(error)
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
request = resourcelocator.sockgenuine + '/v1/marketdata/' + pair
nonce = int(time.time()*1000)
payload = {
    'request': request,
    'nonce': nonce
}
authenticator.authenticate(payload)

# Establish websocket connection.
ws = websocket.WebSocketApp(request, on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})

# Purchase on discount only.
last = Decimal( deal.getvalue() )
if last.compare(0) == 1 :

    # Define trigger and stop loss prices.
    trip = Decimal( last * Decimal( 0.99 ) ).quantize( Decimal('1.00') )
    stop = Decimal( trip * Decimal( 0.99 ) ).quantize( Decimal('1.00') )

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': size,
        'price': str(last),
        'side': 'buy',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = resourcelocator.restsandbox + endpoint
    response = requests.post(request, data = None, headers = headers)
    logger.info(response.json())

    # Hangon a sec.
    time.sleep(1)

    # Construct stop loss order payload.
    # Note that sell orders require the stop_price to be greater than the price.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': size,
        'stop_price': str(trip),
        'price': str(stop),
        'side': 'sell',
        'type': 'exchange stop limit'
    }
    headers = authenticator.authenticate(payload)

    request = resourcelocator.restsandbox + endpoint
    response = requests.post(request, data = None, headers = headers)
    logger.info(response.json())
