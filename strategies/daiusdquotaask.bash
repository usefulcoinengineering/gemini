#! /bin/bash
#
# script name: daiusdquotaask.bash
# script author: munair simpson
# script created: 20210223
# script purpose: ask on DAI using USD on quota

# LONG on USD and SHORT on DAI, where:
# Parameter 0 is the pair.
# Parameter 1 is the budget (1000 is 1000 USD).
# Parameter 2 is the price (450 is 450 USD).
python3 ../quotaask.py DAIUSD 109274.85632323 1 && echo success!
