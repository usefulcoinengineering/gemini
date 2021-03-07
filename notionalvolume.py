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


# Submit request.
logger.debug(f'submitting request...')
post = notionalvolume()
post = post.json()
dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
logger.debug ( dump )

# Let the shell know we successfully made it this far!
if post: sys.exit(0)
else: sys.exit(1)
