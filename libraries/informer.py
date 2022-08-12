#!/usr/bin/env python3
#
# library name: informer.py
# library author: munair simpson
# library created: 20220811
# library purpose: retrieve market data.


import requests
import ssl
import json
import datetime
import time

from decimal import Decimal

from libraries.logger import logger as logger

import libraries.definer as definer
import libraries.authenticator as authenticator

def maximumbid(
        pair: str
    ) -> None:

    # Get the highest bid in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint )
    bidprice = Decimal( response.json()['bid'] )

    # Update logs.
    logger.debug(f'bidprice: {bidprice}')

    return bidprice

def minimumask(
        pair: str
    ) -> None:

    # Get the lowest ask in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint )
    askprice = Decimal( response.json()['ask'] )

    # Update logs.
    logger.debug(f'askprice: {askprice}')

    return askprice