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

tradingpair="ETHUSD"
tradingexit="2400"

read -p "type (trading) pair or press enter to continue with default [$tradingpair]: " tradingpair
read -p "type (trading price level) exit or press enter to continue with default [$tradingexit]: " tradingexit

tradingpair=${tradingpair:-ETHUSD}
tradingexit=${tradingexit:-2400}

python3 ../priceincreasemonitor.py $tradingpair $tradingexit