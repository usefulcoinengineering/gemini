#!/usr/bin/env python3
#
# script name: sendmessage.py
# script author: munair simpson
# script created: 20220819
# script purpose: send message specified.


# Detailed Description:
#  1. Use the messenger library to send the specified information to a Discord channel with a webhook.
#
# Execution:
#   - Use the wrapper BASH script in the "tests" directory.

import sys

from libraries.logger import logger
from libraries.messenger import sendmessage

# Set default message in cause a BASH wrapper has not been used.
message = "Sending a test message from a Python script using a custom (messenger.py) library."

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 2 :
    message = sys.argv[1]
else :
    logger.error ( f'incorrect number of command line arguments. using default value of {message}...' )

# Cancel message.
sendmessagestatus = sendmessage( message )
if sendmessagestatus : sys.exit(0)
else : sys.exit(1)