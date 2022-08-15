#!/usr/bin/env python3


# Warning:
#
# This version of rentseeker is using synchronous communications. This may not be ideal.
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

def bidrise (
        pair: str,
        rise: str
        ) -> None:

    # Define dataset class.
    # Purpose: Stores the offers received during the websocket connection session.
    dataset = []

    # Construct subscription request.
    subscriptionrequest = f'{{"type": "subscribe","subscriptions":[{{"name":"l2","symbols":["{pair}"]}}]}}'

    # Construct payload.
    request = definer.sockserver + '/v2/marketdata'
    nonce = int(time.time()*1000)
    payload = {
        'request': request,
        'nonce': nonce
    }
    authenticator.authenticate(payload)

    # Establish websocket connection.
    ws = create_connection( request )
    ws.send( subscriptionrequest )

    # Set default value for the maximum bid price to zero.
    maximum = Decimal(0)
    
    while True:
        newmessage = ws.recv()
        dictionary = json.loads( newmessage )
        grossmargin = Decimal( rise )

        # Uncomment this statement to debug messages: logger.debug(dictionary)

        # Process "type": "update" messages with events only.
        if 'l2_updates' in dictionary['type']:
            if dictionary['changes'] != []:
                changes = dictionary['changes']

                # Rank bids and determine the highest bid among the changes in the Gemini L2 update response.
                bidranking = [ Decimal(change[1]) for change in changes if change[0] == 'buy' ]
                if bidranking != []:
                    maximum = max(bidranking)
                    dataset.append(maximum)

                    # Define session minimum and average values.
                    sessionmin = Decimal( min(dataset) )
                    sessionavg = Decimal( statistics.mean(dataset) )

                    # Calculate movement away from cost [if any].
                    move = 100 * ( maximum - sessionmin ) / sessionmin

                    # Determine how much the maximum deviates away from the session average.
                    # If it deviated by more than four standard deviations, then do nothing further.
                    # Continue at the start of the loop.
                    deviatedby = maximum - sessionavg
                    if len(dataset) != 1:
                        if deviatedby.compare( 4 * statistics.stdev(dataset) ) == 1:
                            logger.info( f'{move:.2f}% off lows [{sessionmin}] : {pair} is {maximum} presently. Aberration... The mean is: {sessionavg:.2f}. Dumping!' )
                            dataset.pop()
                            continue

                    # Display impact of event information received.
                    logger.info( f'{move:.2f}% off lows [{sessionmin}] : {pair} is {maximum} presently.' )

                    # Define profitable (rent) price.
                    rent = Decimal( sessionmin * ( 1 + grossmargin ) )

                    # Exit loop if profitable.
                    # Return maximum bid.
                    if maximum.compare( rent ) == 1 :
                        text = f'{pair} rose {grossmargin*100}% in price. '
                        text = text + f'It is now {maximum:.2f} on Gemini. '
                        text = text + f'Selling above {rent:.2f} is profitable.'
                        logger.info( text )
                        appalert( text )
                        ws.close()
                        break

    # Return value when profitable only.
    if maximum.compare(0) == 1 : return maximum
    else: return False
