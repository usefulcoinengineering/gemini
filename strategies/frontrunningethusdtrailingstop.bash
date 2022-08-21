#! /bin/bash
#
# script name: frontrunningethusdtrailingstop.bash
# script author: munair simpson
# script created: 20220814
# script purpose: quickly bid and then trail ask on ETH using a fixed amount of ETH (the base currency).

# LONG on ETH and accumulating gains in USD:
# Parameter 0 is the pair ('ETHUSD').
# Parameter 1 is the size (of the order in terms of the base currency, thus 100 is 100 ETH).
# Parameter 2 is the stop price (so 0.003 is a 0.3% fall in the purchase price sets the stop price).
# Parameter 3 is the sell price (so 0.006 is a 0.6% fall in the purchase price sets the sell price).

# Volatile Market: make the stop and sell values much larger.
# Sluggish Market: make the stop and sell values much smaller.

# Production
# python3 ../frontrunningtrailingstop.py ETHUSD 1 0.0500 0.1000

# Testing
# python3 ../frontrunningtrailingstop.py ETHUSD 0.001 0.0050 0.0100

# Gemini's API Transaction Fee
# Presently: 20 basis points (or '0.0020').
# Premium Impact: Always add 0.0020 to the premium desired (in order to offset the fee for selling).
# Discount Impact: Always subtract 0.0020 from the discount desired (in order to offset the fee for buying).

# while [[ True ]]; do
#  python3 ../frontrunningtrailingstop.py ETHUSD 0.001 0.0050 0.0100
# done

python3 ../frontrunningtrailingstop.py ETHUSD 0.5 0.0013 0.0037