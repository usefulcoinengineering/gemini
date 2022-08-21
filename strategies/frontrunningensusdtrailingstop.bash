#! /bin/bash
#
# script name: frontrunningensusdtrailingstop.bash
# script author: munair simpson
# script created: 20220817
# script purpose: quickly bid and then trail ask on ENS using a fixed amount of ENS (the base currency).

# LONG on ENS and accumulating gains in USD:
# Parameter 0 is the pair ('ENSUSD').
# Parameter 1 is the size (of the order in terms of the base currency, thus 100 is 100 ENS).
# Parameter 2 is the stop price (so 0.003 is a 0.3% fall in the purchase price sets the stop price).
# Parameter 3 is the sell price (so 0.006 is a 0.6% fall in the purchase price sets the sell price).

# Volatile Market: make the stop and sell values much larger.
# Sluggish Market: make the stop and sell values much smaller.

# Production
# python3 ../frontrunningtrailingstop.py ENSUSD 1 0.0500 0.1000

# Testing
# python3 ../frontrunningtrailingstop.py ENSUSD 0.001 0.0050 0.0100

# Gemini's API Transaction Fee
# Presently: 20 basis points (or '0.0020').
# Premium Impact: Always add 0.0020 to the premium desired (in order to offset the fee for selling).
# Discount Impact: Always subtract 0.0020 from the discount desired (in order to offset the fee for buying).

# while [[ True ]]; do
#  python3 ../frontrunningtrailingstop.py ENSUSD 0.001 0.0050 0.0100
# done

python3 ../frontrunningtrailingstop.py ENSUSD 1 0.0025 0.0050