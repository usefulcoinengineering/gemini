#! /bin/bash
#
# script name: discountethusdquotabid.bash
# script author: munair simpson
# script created: 20201120
# script purpose: bid on BTC using USD on quota

# LONG on BTC and SHORT on USD, where:
# Parameter 0 is the pair.
# Parameter 1 is the budget (100 is 100 USD).
# Parameter 2 is the discount (0.02 is a 2% discount).
python3 ../discountquotafrontrunningbid.py BTCUSD 10000 0.005 && echo success!
