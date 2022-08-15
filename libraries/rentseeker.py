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

    # Set the highest bid to zero.
    maximumbid = Decimal(0)

    # Set bid price at which to exit the loop.
    exitprice = Decimal(rise)
    
    while True:
        newmessage = ws.recv()
        dictionary = json.loads( newmessage )
        
        # Uncomment this statement to debug messages: logger.debug(dictionary)

        # Process "type": "update" messages with events only.
        if 'l2_updates' in dictionary['type']:
            if dictionary['changes'] != []:
                changes = dictionary['changes']

                # Rank bids and determine the highest bid among the changes in the Gemini L2 update response.
                bidranking = [ Decimal(change[1]) for change in changes if change[0] == 'buy' ]
                if bidranking != [] :
                    
                    # Define highest offer price.
                    maximumbid = max(bidranking)
                    
                    # Filter out aberrations.
                    # Add to a defined dataset.
                    dataset.append(maximumbid)
                    
                    # Determine how much the maximum bid fluctuated away from the session average.
                    # If it deviated by more than four standard deviations, then do nothing further.
                    # Continue at the start of the while loop.
                    sessionavg = Decimal( statistics.mean(dataset) )
                    fluctuated = 100 * ( maximumbid - sessionavg ) / sessionavg
                    deviatedby = maximumbid - sessionavg
                    deviatedby = abs(deviatedby)
                    if len(dataset) != 1:
                        if deviatedby.compare( 4 * statistics.stdev(dataset) ) == 1:
                            fragmentone = f'{maximumbid} was offered to buy {pair[:3]}. '
                            fragmenttwo = f'It is more than four standard deviations off the {sessionavg:.2f} session average. '
                            logger.info( f'{fragmentone}{fragmenttwo} The {fluctuated:.2f}% fluctuation is aberratic... Dumping!' )
                            dataset.pop()
                            continue
                        continue

                    # Display impact of event information received.
                    logger.info( f'Traders are offering {maximumbid} for {pair[:3]}.' )    
                    
                    # Exit loop if profitable.
                    if maximumbid.compare( exitprice ) == 1 :
                        text = f'{pair[:3]} above {exitprice:.2f} {pair[3:]} is defined as profitable.'
                        text = text + f'It is now {maximumbid:.2f} {pair[3:]} on Gemini. Exiting loop and closing websocket.'
                        logger.info( text )
                        appalert( text )
                        ws.close()
                        break

    # Return value when profitable only.
    if maximumbid.compare(0) == 1 : return maximumbid
    else: return False