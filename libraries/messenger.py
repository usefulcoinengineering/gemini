#!/usr/bin/env python3


import json
import boto3

from libraries.logger import logger

# Create AWS SNS client
snsclient = boto3.client('sns')

# Define alert function
def smsalert( message ):
    # Send message via SMS.
    snsresponse = snsclient.publish( PhoneNumber='+12062270634', Message=message )
    responseout = json.dumps( snsresponse, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( f'Response to SNS Request:\n{responseout}' )
    # Log SMS execution details
