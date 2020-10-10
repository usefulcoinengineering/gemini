#!/usr/bin/env python3


# Warning:
#
# This version of rentseeker is using synchronous communications. This may not be ideal.
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

def bidrise (
        pair: str,
        rise: str
        ) -> None:

    # Define Cost class.
    # Purpose: Stores the cost price used to determine gains.
    class Cost:
        def __init__(self, price): self.__price = price
        def getvalue(self): return self.__price
        def setvalue(self, price): self.__price = price

    # Instantiate Cost object.
    cost = Cost(0)

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
        grossmargin = Decimal( rise )
        investment = Decimal( cost.getvalue() )

        # Uncomment this statement to debug messages: logger.debug(dictionary)

        # Process "type": "update" messages with events only.
        if 'l2_updates' in dictionary['type']:
            if dictionary['changes'] != []:
                changes = dictionary['changes']

                # Rank bids and determine the highest bid among the changes in the Gemini L2 update response.
                bidranking = [ Decimal(change[1]) for change in changes if change[0] == 'buy' ]
                if bidranking != []:
                    maximumbid = max(bidranking)

                    # Define investment.
                    # Use first maximum.
                    if investment == 0:
                        investment = maximumbid
                        cost.setvalue( maximumbid )

                    # Calculate movement away from cost [if any].
                    move = 100 * ( maximumbid - investment ) / investment

                    # Display impact of event information received.
                    logger.info( f'{pair} is {maximumbid} presently: a {move:.2f}% away from {investment}.' )

                    # Define bargain (sale) price.
                    sale = Decimal( investment * ( 1 + grossmargin ) )

                    # Exit loop if profitabl.
                    if maximumbid.compare( sale ) == 1 :
                        text = f'{pair} rose {grossmargin*100}% in price. '
                        text = text + f'It is now {maximumbid:.2f} on Gemini. '
                        text = text + f'Selling above {sale:.2f} is profitable.'
                        logger.info( text )
                        smsalert( text )
                        ws.close()
                        break

    # Return value on discount only.
    last = Decimal( deal.getvalue() )
    if last.compare(0) == 1 :
        return last
    else: return False
