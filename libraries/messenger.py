#!/usr/bin/env python3


import json
import requests

import libraries.constants as constants
from libraries.logger import logger

# Define alert function
def appalert( message ):
    # Send message to Discord server.
    appresponse = requests.post( constants.discordwebhook, data = json.dumps( { "content": message } ), headers = { 'Content-Type': 'application/json' } )
    logger.debug ( f'Response to Discord Request:\n{appresponse}' )
    # Log execution details