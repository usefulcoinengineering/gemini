#! /bin/bash
#
# script name: btcdaiquotabid.bash
# script author: munair simpson
# script created: 20210223
# script purpose: bid on btc using DAI on quota

# LONG on BTC and SHORT on DAI, where:
# Parameter 0 is the pair.
# Parameter 1 is the budget (1000 is 1000 DAI).
# Parameter 2 is the price (450 is 450 DAI).
python3 ../quotabid.py BTCDAI 10000 48313 && echo success!
