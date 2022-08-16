#!/usr/bin/env python3
#
# library name: informer.py
# library author: munair simpson
# library created: 20220811
# library purpose: retrieve market data.


import requests
import json

from decimal import Decimal

from libraries.logger import logger as logger
from libraries.messenger import appalert as appalert

import libraries.definer as definer
import libraries.authenticator as authenticator

def maximumbid(
        pair: str
    ) -> None:

    # Get the highest bid in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint )
    response = response.json()
    datadump = json.dumps( response, sort_keys=True, indent=4, separators=(',', ': ') )

    # Write the dump to logs.
    logger.debug ( datadump )

    # Send notice if error arises.
    if response["result"] == "error" :
        appalert ( f'\"{datadump["reason"]}\" {datadump["result"]}: {datadump["message"]}' )

        # Exit returning a boolean value of "False".
        return False

    else:
        # Update logs and return bid price as a string.
        bidprice = Decimal( response.json()['bid'] )
        logger.debug( f'bidprice: {bidprice}' )
        return str(bidprice)

def minimumask(
        pair: str
    ) -> None:

    # Get the lowest ask in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint )
    response = response.json()
    datadump = json.dumps( response, sort_keys=True, indent=4, separators=(',', ': ') )
    
    
    # Write the dump to logs.
    logger.debug ( datadump )

    # Send notice if error arises.
    if response["result"] == "error" :
        appalert ( f'\"{datadump["reason"]}\" {datadump["result"]}: {datadump["message"]}' )

        # Exit returning a boolean value of "False".
        return False

    else:
        # Update logs and return ask price as a string.
        askprice = Decimal( response.json()['ask'] )
        logger.debug( f'askprice: {askprice}' )
        return str(askprice)