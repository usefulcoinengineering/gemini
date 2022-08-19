#!/usr/bin/env python3
#
# library name: messenger.py
# library author: munair simpson
# library created: 20220819
# library purpose: continually monitor ask prices via Gemini's Websockets API until the exit threshold is breached.
# library legacy: originally "dealseeker.py" because it waited on a fall from websocket session highs.

import json
import requests

from libraries.logger import logger

import libraries.credentials as credentials

# Define alert function
def sendmessage( message ):
    # Send message to Discord server.
    appresponse = requests.post( credentials.discordwebhook, data = json.dumps( { "content": message } ), headers = { 'Content-Type': 'application/json' } )
    logger.debug ( f'Response to Discord Request:\n{appresponse}' )
    # Log execution details