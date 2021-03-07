#!/usr/bin/env python3


# Strategy Outline:
#  1. Retrieve the 30-day (USD-denominated) notional volume and trading fees.
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json
import requests

from libraries.logger import logger
from libraries.volumizer import notionalvolume


# Set bid size ['0.1' is the minimum for DAIUSD].
field = 'notional_30d_volume'

# Override defaults with command line parameters.
if len(sys.argv) == 2:
    field = sys.argv[1]

# Submit request.
logger.debug(f'submitting request...')
post = notionalvolume()

# Display desired field (or everything received).
if field == '': post = post.json()
else: post = post.json()[field]

# Format response.
dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
logger.info ( dump )

# Let the shell know we successfully made it this far!
if post: sys.exit(0)
else: sys.exit(1)
