#!/usr/bin/env python3
#
# script name: tradingvolume.py
# script author: munair simpson
# script created: 20220819
# script purpose: retrieve the notional trading volume of the account using Gemini's REST API.

# Strategy Outline:
#  1. Retrieve the 30-day (USD-denominated) notional volume.
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json

from libraries.logger import logger
from libraries.messenger import sendmessage
from libraries.volumizer import notionalvolume

# Submit request.
logger.debug ( f'Submitting request...' )
jsonresponse = notionalvolume().json()

# Remove comments to debug.
# jsondatadump = json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(',', ': ') )
# logger.debug ( jsondatadump )

# Format Report.
tradinginfo = f'Notional 30 day Trading Volume: {jsonresponse["notional_30d_volume"]:,.2f} USD. '
logger.info = f'{tradinginfo}'
sendmessage ( f'{tradinginfo}' )

# Let the shell know we successfully made it this far!
sys.exit(0)