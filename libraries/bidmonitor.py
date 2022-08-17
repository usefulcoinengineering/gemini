#!/usr/bin/env python3
#
# library name: bidmonitor.py
# library author: munair simpson
# library created: 20220811
# library purpose: continually monitor bid prices via Gemini's Websockets API.


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

def anchoredrise (
        pair: str,
        rise: str
        ) -> None:

    # Function Description:
    #  1. Open a websocket connection.
    #  2. Request L2 orderbook data.
    #  3. Monitor the orderbook for a rise in bids (i.e. "prices offered to acquire the asset") for the pair specified.
    #  4. Send an alert to a Discord channel via the messenger library's webhook when bid prices surpass the specified threshold.
    #
    # Function Purpose: 
    #     Waiting for an absolute rise in bid prices.
    #
    # Arguments:
    #  1. pair is the trading pair monitored.
    #  2. rise is the rise in ask prices (specified in decimal terms) required to rise the loop and close the websocket.
    # 
    # Execution:
    #   - from libraries.bidmonitor import anchoredrise
    #   - highestbid = anchoredrise( "BTCUSD", "0.004" )

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
    anchoredrise = Decimal(rise)
    
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
                            fragmentone = f'A trader just offered {maximumbid} to buy {pair[:3]}. That bid is odd. '
                            fragmenttwo = f'It is more than four standard deviations from average bids [{sessionavg:.2f}]. '
                            logger.info( f'{fragmentone}{fragmenttwo} The {fluctuated:.2f}% fluctuation is aberratic... Dumping!' )
                            dataset.pop()
                            continue

                    # Display impact of event information received.
                    logger.info( f'A trader just offered {maximumbid} to buy {pair[:3]}.' )    
                    
                    # Exit loop if profitable.
                    if maximumbid.compare( anchoredrise ) == 1 :
                        notice = f'Exiting loop and closing websocket. {pair[:3]} above {anchoredrise:.2f} {pair[3:]}. '
                        notice = notice + f'It is now {maximumbid:.2f} {pair[3:]}. '
                        notice = notice + f'This is sufficiently profitable to warrant submiting a stop limit order to lock in gains. '
                        logger.info( notice )
                        appalert( notice )
                        ws.close()
                        break

    # Return value when profitable only.
    if maximumbid.compare(0) == 1 : return maximumbid
    else: return False