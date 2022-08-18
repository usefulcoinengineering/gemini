#!/usr/bin/env python3
#
# script name: pricedecreasemonitor.py
# script author: munair simpson
# script created: 20220818
# script purpose: use websockets to continually monitor a trading pair for a decrease in price levels.

# Detailed Description:
#  1. Use the takermonitor library to request the required information.
#  2. Print the results using the logger library.
#  3. Send an alert to a Discord channel using the messenger library's webhook.
#
# Execution:
#   - Use the wrapper BASH script in the "tests" directory.

import sys

from libraries.logger import logger
from libraries.takermonitor import decreasemonitor
from libraries.messenger import appalert as appalert

# Set default trading pair and loop exit price in case a BASH wrapper has not been used.
pair = "ETHUSD"
exit = "2000"

# Override defaults with command line parameters from BASH wrapper.
if len( sys.argv ) == 3 :
    pair = sys.argv[1]
    exit = sys.argv[2]
else :
    logger.warning ( f'incorrect number of command line arguments. using default values of a {exit} price level for {pair}...' )

# Define tradeprice class.
# Purpose: Stores the state of the price of the last trade.
class Tradeprice:
    def __init__(self, state): self.__state = state
    def getvalue(self): return self.__state
    def setvalue(self, state): self.__state = state

# Define trademaker class.
# Purpose: Stores the state of the maker side of the last trade.
class Trademaker:
    def __init__(self, state): self.__state = state
    def getvalue(self): return self.__state
    def setvalue(self, state): self.__state = state

# Initialize tradeprice and trademaker values.
tradeprice = Tradeprice( '' )
trademaker = Trademaker( '' )

# Enter price monitor loop.
orderstatus = decreasemonitor( pair=pair, exit=exit, tradeprice=tradeprice, trademaker=trademaker )

if trademaker == "bid" : appalert ( f'{tradeprice} {pair[:3]} purchased. ' )
if trademaker == "ask" : appalert ( f'{tradeprice} {pair[:3]} sold. ' )
if orderstatus : sys.exit( 0 )
else : sys.exit( 1 )