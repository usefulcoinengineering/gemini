#! /bin/bash
#
# script name: priceincreasemonitor.bash
# script author: munair simpson
# script created: 20220817
# script purpose: wrapper for priceincreasemonitor.py

# Use websockets to continually monitor a trading pair for an increase in price levels.
# Parameter 0 is the trading pair monitored for price increases.
# Parameter 1 is the price that must be breached to exit the price monitor loop.

# Execution:
# python3 ../priceincreasemonitor.py ETHUSD 24000

python3 ../priceincreasemonitor.py ETHUSD 2400