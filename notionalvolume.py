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
field = ''

# Override defaults with command line parameters.
if len(sys.argv) == 2:
    field = sys.argv[1]

# Submit request.
logger.debug(f'submitting request...')
post = notionalvolume()

# Format response.
if field == 'notional_30d_volume': print( f'notional 30-day volume is {locale.currency( 100000, grouping=True )}.' )
if field == 'api_maker_fee_bps': print( f'the fee that Gemini is charging you for making orders via the API is {post.json()[field]} basis points.' )
if field == '':
    dump = json.dumps( post.json(), sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( dump )


# Let the shell know we successfully made it this far!
if post: sys.exit(0)
else: sys.exit(1)
