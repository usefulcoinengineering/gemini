#!/usr/bin/env python3
#
# library name: pricegetter.py
# library author: munair simpson
# library created: 20220811
# library purpose: retrieve market data using the Gemini REST API.


import requests
import json

from decimal import Decimal

from libraries.logger import logger as logger
from libraries.messenger import sendmessage as sendmessage

import libraries.definer as definer
import libraries.authenticator as authenticator

def ticker(
        pair: str
    ) -> None:

    # Get the latest prices and trading volumes.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint ).json()

    # Uncomment to write the response to logs: 
    logger.debug ( json.dumps( response, sort_keys=True, indent=4, separators=(',', ': ') ) )
 
    return response