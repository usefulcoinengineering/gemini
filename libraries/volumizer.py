#!/usr/bin/env python3
#
# library name: volumizer.py
# library author: munair simpson
# library created: 20210307
# library purpose: retrieve trading activity dependent data for the last 30 days across all pairs traded


import requests
import datetime
import time

from libraries.logger import logger as logger

import libraries.definer as definer
import libraries.authenticator as authenticator

def notionalvolume() -> None:

    # Retrieve activity based data 
    # like transaction fees and 
    # trading volume (USD terms).
    endpoint = '/v1/notionalvolume'
    t = datetime.datetime.now()
    payload = {
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'request': endpoint
    }
    headers = authenticator.authenticate(payload)

    request = definer.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response
