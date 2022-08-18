#!/usr/bin/env python3
#
# library name: askmonitor.py
# library author: munair simpson
# library created: 20220811
# library purpose: continually monitor ask prices via Gemini's Websockets API until the exit threshold is breached.
# library legacy: originally "dealseeker.py" because it waited on a fall from websocket session highs.


# Warning:
#
# This version of askmonitor is using synchronous communications. This may not be ideal.
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
from libraries.messenger import sendmessage as sendmessage

import libraries.definer as definer
import libraries.authenticator as authenticator

def floatingfall (
        pair: str,
        fall: str
        ) -> None:

    # Function Description:
    #  1. Open a websocket connection.
    #  2. Request L2 orderbook data.
    #  3. Monitor the orderbook for a fall in asks (i.e. the "selling prices offered") for pair parameter specified.
    #  4. Send an alert to a Discord channel using the messenger library's webhook when asks fall from session highs.
    #
    # Function Purpose: 
    #     Waiting for an relative fall in ask prices.
    # 
    # Arguments:
    #  1. pair is the trading pair monitored.
    #  2. fall is the fall in ask prices (specified in decimal terms) required to exit the loop and close the websocket.
    # 
    # Execution:
    #   - from libraries.askmonitor import floatingfall
    #   - lowestask = floatingfall( "BTCUSD", "0.004" )

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

    # Set default value for the minimum ask price to zero.
    minimumask = Decimal(0)

    while True:
        newmessage = ws.recv()
        dictionary = json.loads( newmessage )
        percentoff = Decimal( fall )

        # Uncomment this statement to debug messages: logger.debug(dictionary)

        # Process "type": "update" messages with events only.
        if 'l2_updates' in dictionary['type']:
            if dictionary['changes'] != []:
                changes = dictionary['changes']

                # Rank asks and determine the lowest ask among the changes in the Gemini L2 update response.
                askranking = [ Decimal(change[1]) for change in changes if change[0] == 'sell' ]
                if askranking != []:
                    minimumask = min(askranking)
                    dataset.append(minimumask)

                    # Define session maximum and average values.
                    sessionmax = Decimal( max(dataset) )
                    sessionavg = Decimal( statistics.mean(dataset) )

                    # Calculate movement away from high [if any].
                    move = 100 * ( sessionmax - minimumask ) / sessionmax

                    # Determine how much the minimum deviates away from the session average.
                    # If it deviated by more than four standard deviations, then do nothing further.
                    # Continue at the start of the loop.
                    deviatedby = minimumask - sessionavg
                    if len(dataset) != 1:
                        if deviatedby.compare( 4 * statistics.stdev(dataset) ) == 1:
                            logger.info( f'{move:.2f}% off highs [{sessionmax}] : {pair} is {minimumask} presently. Aberration... The mean is: {sessionavg:.2f}. Dumping!' )
                            dataset.pop()
                            continue

                    # Display impact of event information received.
                    logger.info( f'{move:.2f}% below highs [{sessionmax}] : {pair} is {minimumask} presently.' )

                    # Define bargain (sale) price.
                    sale = Decimal( sessionmax * ( 1 - percentoff ) )

                    # Exit loop and set "deal"...
                    # Only if there's a sale (bargain) offer.
                    if sale.compare( minimumask ) == 1 :
                        text = f'{pair[:3]} fell {percentoff*100}% in price. '
                        text = text + f'It is now {minimumask:.2f} {pair[3:]} on Gemini. '
                        text = text + f'{pair[:3]} at {sale:.2f} {pair[3:]} or lower is defined as a deal.'
                        logger.info( text )
                        sendmessage( text )
                        ws.close()
                        break

        # Return value on discount only.
        if minimumask.compare(0) == 1 : return minimumask
        else: return False

def anchoredfall (
        pair: str,
        fall: str
        ) -> None:

    # Function Description:
    #  1. Open a websocket connection.
    #  2. Request L2 orderbook data.
    #  3. Monitor the orderbook for a fall in asks (i.e. the "selling prices offered") for pair parameter specified.
    #  4. Send an alert to a Discord channel using the messenger library's webhook when asks fall.
    #
    # Function Purpose: 
    #     Waiting for an absolute fall in ask prices.
    #
    # Arguments:
    #  1. pair is the trading pair monitored.
    #  2. fall is the fall in ask prices (specified in decimal terms) required to exit the loop and close the websocket.
    # 
    # Execution:
    #   - from libraries.askmonitor import anchoredfall
    #   - lowestask = anchoredfall( "BTCUSD", "0.004" )

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

    # Set default value for the minimum ask price to zero.
    minimumask = Decimal(0)

    while True:
        newmessage = ws.recv()
        dictionary = json.loads( newmessage )
        percentoff = Decimal( fall )

        # Uncomment this statement to debug messages: logger.debug(dictionary)

        # Process "type": "update" messages with events only.
        if 'l2_updates' in dictionary['type']:
            if dictionary['changes'] != []:
                changes = dictionary['changes']

                # Rank asks and determine the lowest ask among the changes in the Gemini L2 update response.
                askranking = [ Decimal(change[1]) for change in changes if change[0] == 'sell' ]
                if askranking != []:
                    minimumask = min(askranking)
                    dataset.append(minimumask)

                    # Define session maximum and average values.
                    sessionmax = Decimal( max(dataset) )
                    sessionavg = Decimal( statistics.mean(dataset) )

                    # Calculate movement away from high [if any].
                    move = 100 * ( sessionmax - minimumask ) / sessionmax

                    # Determine how much the minimum deviates away from the session average.
                    # If it deviated by more than four standard deviations, then do nothing further.
                    # Continue at the start of the loop.
                    deviatedby = minimumask - sessionavg
                    if len(dataset) != 1:
                        if deviatedby.compare( 4 * statistics.stdev(dataset) ) == 1:
                            logger.info( f'{move:.2f}% off highs [{sessionmax}] : {pair} is {minimumask} presently. Aberration... The mean is: {sessionavg:.2f}. Dumping!' )
                            dataset.pop()
                            continue

                    # Display impact of event information received.
                    logger.info( f'{move:.2f}% below highs [{sessionmax}] : {pair} is {minimumask} presently.' )

                    # Define bargain (sale) price.
                    sale = Decimal( sessionmax * ( 1 - percentoff ) )

                    # Exit loop and set "deal"...
                    # Only if there's a sale (bargain) offer.
                    if sale.compare( minimumask ) == 1 :
                        text = f'{pair[:3]} fell {percentoff*100}% in price. '
                        text = text + f'It is now {minimumask:.2f} {pair[3:]} on Gemini. '
                        text = text + f'{pair[:3]} at {sale:.2f} {pair[3:]} or lower is defined as a deal.'
                        logger.info( text )
                        sendmessage( text )
                        ws.close()
                        break

        # Return value on discount only.
        if minimumask.compare(0) == 1 : return minimumask
        else: return False