#! /bin/bash
#
# script name: daiusdquotabid.bash
# script author: munair simpson
# script created: 20202023
# script purpose: bid on DAI using USD on quota

# LONG on DAI and SHORT on USD, where:
# Parameter 0 is the pair.
# Parameter 1 is the budget (100 is 100 USD).
# Parameter 2 is the price (450 is 450 USD).
python3 ../quotabid.py DAIUSD 60576.13 1713.76 && echo success!
