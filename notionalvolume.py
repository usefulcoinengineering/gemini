#!/usr/bin/env python3
#
# script name: notionalvolume.py
# script author: munair simpson
# script created: 20220819
# script purpose: retrieve the notional trading volume of the account using Gemini's REST API.

# Strategy Outline:
#  1. Retrieve the 30-day (USD-denominated) notional volume and API trading fee.
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json

from libraries.logger import logger
from libraries.volumizer import notionalvolume

# Submit request.
logger.debug(f'submitting request...')
post = notionalvolume()
data = post.json()
dump = json.dumps( data, sort_keys=True, indent=4, separators=(',', ': ') )

# Format response.
logger.info( f'Notional 30 day trading volume: {post.json()["notional_30d_volume"]:} USD. ' )
logger.info( f'The API transaction fees: {post.json()["api_maker_fee_bps"]} basis points. ' )

# Let the shell know we successfully made it this far!
sys.exit(0)