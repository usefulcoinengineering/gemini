#! /bin/bash
#
# script name: pricedecreasemonitor.bash
# script author: munair simpson
# script created: 20220817
# script purpose: wrapper for pricedecreasemonitor.py

# Use websockets to continually monitor a trading pair for a decrease in price levels.
# Parameter 0 is the trading pair monitored for price decreases.
# Parameter 1 is the price that must be breached to exit the price monitor loop.

# Execution:
# python3 ../pricedecreasemonitor.py ETHUSD 24000

python3 ../pricedecreasemonitor.py ETHUSD 2400