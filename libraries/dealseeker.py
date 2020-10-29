#!/usr/bin/env python3


# Warning:
#
# This version of dealseeker is using synchronous communications. This may not be ideal.
# If the messages are processed faster than they are received, this code is good. If not,
# you are going to lose money.
#
# According to https://pypi.org/project/websocket_client/ [Short-lived one-off send-receive]:
# This is if you want to communicate a short message and disconnect immediately when done.


import requests
import ssl
import json
import datetime
import time

from decimal import Decimal
from websocket import create_connection

from libraries.logger import logger as logger
from libraries.messenger import smsalert as smsalert

import libraries.authenticator as authenticator
import libraries.resourcelocator as resourcelocator

def askfall (
        pair: str,
        drop: str
        ) -> None:

    # Define high class.
    # Purpose: Stores the highest ask offer reached during the websocket connection session.
    class High:
        def __init__(self, price): self.__price = price
        def getvalue(self): return self.__price
        def setvalue(self, price): self.__price = price

    # Define Roll count class.
    # Purpose: Stores the tally of Highs during the websocket connection session.
    class Roll:
        def __init__(self, count): self.__count = count
        def getvalue(self): return self.__count
        def setvalue(self, count): self.__count = count

    # Define deal class.
    # Purpose: Stores the (i)deal (last) ask offered during the websocket connection session.
    class Deal:
        def __init__(self, price): self.__price = price
        def getvalue(self): return self.__price
        def setvalue(self, price): self.__price = price

    # Instantiate high/deal/roll objects.
    high = High(0)
    deal = Deal(0)
    roll = Roll(0)

    # Construct subscription request.
    subscriptionrequest = f'{{"type": "subscribe","subscriptions":[{{"name":"l2","symbols":["{pair}"]}}]}}'

    # Construct payload.
    request = resourcelocator.sockserver + '/v2/marketdata'
    nonce = int(time.time()*1000)
    payload = {
        'request': request,
        'nonce': nonce
    }
    authenticator.authenticate(payload)

    # Establish websocket connection.
    ws = create_connection( request )
    ws.send( subscriptionrequest )
    while True:
        newmessage = ws.recv()
        dictionary = json.loads( newmessage )
        percentoff = Decimal( drop )
        averagemax = Decimal( high.getvalue() )

        # Uncomment this statement to debug messages: logger.debug(dictionary)

        # Process "type": "update" messages with events only.
        if 'l2_updates' in dictionary['type']:
            if dictionary['changes'] != []:
                changes = dictionary['changes']

                # Rank asks and determine the lowest ask among the changes in the Gemini L2 update response.
                askranking = [ Decimal(change[1]) for change in changes if change[0] == 'sell' ]
                if askranking != []:
                    minimumask = min(askranking)

                    # Determine if the ask is a new session high.
                    if minimumask.compare( Decimal(averagemax) ) == 1 :

                            # If so, set the initial high (when roll's value is zero).
                            if not roll.getvalue(): initialmax = minimumask

                            # Also, update "high" (average high).
                            sessionsum = ( averagemax * Decimal( roll.getvalue() ) + minimumask )
                            averagemax = sessionsum  / ( Decimal( roll.getvalue() ) + 1 )

                            # Finally, update objects.
                            high.setvalue( minimumask )
                            roll.setvalue( roll.getvalue() + 1 )


                    # Calculate movement away from high [if any].
                    move = 100 * ( averagemax - minimumask ) / averagemax

                    # Display impact of event information received.
                    logger.info( f'{move:.2f}% off average highs [{averagemax}] : {pair} is {minimumask} presently.' )

                    # Define bargain (sale) price.
                    sale = min( Decimal( averagemax * ( 1 - percentoff ) ), Decimal( initialmax * ( 1 - percentoff ) ) )

                    # Exit loop and set "deal"...
                    # Only if there's a sale (bargain) offer.
                    if sale.compare( minimumask ) == 1 :
                        logger.info( f'{pair} [now {minimumask:.2f}] just went on sale [dropped below {sale:.2f}].' )
                        smsalert( f'There was a {percentoff*100}% drop in the price of the {pair} pair on Gemini.' )

                        # Update deal price.
                        deal.setvalue(minimumask)
                        ws.close()
                        break

    # Return value on discount only.
    last = Decimal( deal.getvalue() )
    if last.compare(0) == 1 :
        return last
    else: return False

def pricedrop(
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
        averagemax = Decimal( high.getvalue() )
        # Uncomment this statement to debug messages:
        logger.debug(dictionary)

        # Process "type": "update" messages with events only.
        if 'update' in dictionary['type']:
            if dictionary['events'] != []:
                events = dictionary['events']

                # Process "type": "trade" events for latest price.
                for event in events:
                    if event['type'] == 'trade' : last = Decimal( event["price"] )
                    if last.compare( Decimal(averagemax) ) == 1 :
                        averagemax = last
                        high.setvalue(last)

                    # Calculate movement away from high [if any].
                    move = 100 * ( averagemax - last ) / averagemax

                    # Display impact of event information received.
                    logger.info( f'{move:.2f}% off highs [{averagemax}] : {pair} is {last} presently : [Message ID: {dictionary["socket_sequence"]}].' )

                    # Define bargain (sale) price.
                    sale = Decimal( averagemax * ( 1 - percentoff ) )

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
