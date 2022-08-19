#!/usr/bin/env python3
#
# script name: transactionfee.py
# script author: munair simpson
# script created: 20220819
# script purpose: retrieve the transaction fee of the account using Gemini's REST API.

# Strategy Outline:
#  1. Retrieve the present API transaction fee.
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
tradinginfo = f'Present API transaction fee: {jsonresponse["api_maker_fee_bps"]} basis points.'
logger.info = f'{tradinginfo}'
sendmessage ( f'{tradinginfo}' )

# Let the shell know we successfully made it this far!
sys.exit(0)