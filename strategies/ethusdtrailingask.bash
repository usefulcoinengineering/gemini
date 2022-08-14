#! /bin/bash
#
# script name: ethusdtrailingask.bash
# script author: munair simpson
# script created: 20220814
# script purpose: quickly bid and then trail ask on ETH using a fixed amount of ETH (the base currency).

# LONG on ETH and accumulating gains in USD:
# Parameter 0 is the pair.
# Parameter 1 is the size (of the order in terms of the base currency, thus 100 is 100 ETH).
# Parameter 2 is the price that trips the initial stop order (so 0.003 is a 0.3% rise in the purchase price).
# Parameter 3 is the stop price that forces the submission of an ask (so 0.007 is a 0.7% gain on the purchase price).

# Volatile Market: make the trip much more than the stop.
# Sluggish Market: make the trip can be much closer to the stop.

# Production
# python3 ../frontrunningbidtrailingstop.py ETHUSD 1 0.0578 0.0137

# Testing
# python3 ../frontrunningbidtrailingstop.py ETHUSD 0.001 0.0037 0.0013

# Gemini's API Transaction Fee
# Presently: 20 basis points (or '0.002').
# Premium Impact: Always add 0.002 to the premium desired (in order to offset the fee for selling).
# Discount Impact: Always subtract 0.002 from the discount desired (in order to offset the fee for buying).

# while [[ True ]]; do
#  python3 ../frontrunningbidtrailingstop.py ETHUSD 0.001 0.0037 0.0013
# done

python3 ../frontrunningbidtrailingstop.py ETHUSD 0.001 0.0037 0.0013