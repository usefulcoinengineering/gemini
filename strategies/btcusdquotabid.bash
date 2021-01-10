#! /bin/bash
#
# script name: btcusdquotabid.bash
# script author: munair simpson
# script created: 20210110
# script purpose: bid on btc using USD on quota

# LONG on BTC and SHORT on USD, where:
# Parameter 0 is the pair.
# Parameter 1 is the budget (100 is 100 USD).
# Parameter 2 is the price (450 is 450 USD).
python3 ../quotabid.py BTCUSD 10000 19000 && echo success!
