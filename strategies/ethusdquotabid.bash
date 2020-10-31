#! /bin/bash
#
# script name: ethusdquotabid.bash
# script author: munair simpson
# script created: 20201022
# script purpose: bid on ETH using USD on quota

# LONG on ETH and SHORT on USD, where:
# Parameter 0 is the pair.
# Parameter 1 is the budget (100 is 100 USD).
# Parameter 2 is the price (450 is 450 USD).
python3 ../quotabid.py ETHUSD 500 417.76 && echo success!
