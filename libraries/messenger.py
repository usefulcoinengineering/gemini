#!/usr/bin/env python3


import json
import requests

import libraries.credentials as credentials
from libraries.logger import logger

# Define alert function
def sendmessage( message ):
    # Send message to Discord server.
    appresponse = requests.post( credentials.discordwebhook, data = json.dumps( { "content": message } ), headers = { 'Content-Type': 'application/json' } )
    logger.debug ( f'Response to Discord Request:\n{appresponse}' )
    # Log execution details