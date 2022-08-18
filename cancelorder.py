#!/usr/bin/env python3
#
# script name: cancelorder.py
# script author: munair simpson
# script created: 20220816
# script purpose: cancel order number specified.


# Detailed Description:
#  1. Use the ordermanager library to request the required information.
#  2. Print the results using the logger library.
#  3. Send an alert to a Discord channel using the messenger library's webhook.
#
# Execution:
#   - Use the wrapper BASH script in the "tests" directory.

import sys

from libraries.logger import logger
from libraries.ordermanager import cancelorder
from libraries.messenger import appalert as appalert

# Set trading default trading pair in cause a BASH wrapper has not been used.
order = 136457975606

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 2 :
    order = sys.argv[1]
else :
    logger.debug ( f'incorrect number of command line arguments. using default value of {order}...' )

# Cancel order.
orderstatus = cancelorder( order )
if orderstatus : sys.exit(0)
else : sys.exit(1)