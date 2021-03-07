#!/usr/bin/env python3


# Strategy Outline:
#  1. Retrieve the 30-day (USD-denominated) notional volume and trading fees.
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json
import requests
import locale

from libraries.logger import logger
from libraries.volumizer import notionalvolume


# Set locale and default field value.
locale.setlocale( locale.LC_ALL, '' )
field = 'notional_30d_volume'

# Override defaults with command line parameters.
if len(sys.argv) == 2:
    field = sys.argv[1]

# Submit request.
logger.debug(f'submitting request...')
post = notionalvolume()

# Display desired field (or everything received).
if field == '':
    post = post.json()

    # Format response.
    dump = json.dumps( post, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.info ( dump )

else:
    post = post.json()[field]
    # Format response.
    if field == 'notional_30d_volume': print( f'notional 30-day volume is {locale.currency( post, grouping=True )}.' )
    if field == 'api_maker_fee_bps': print( f'the fee that Gemini is charging you for making orders via the API is {post} basis points.' )

# Let the shell know we successfully made it this far!
if post: sys.exit(0)
else: sys.exit(1)
