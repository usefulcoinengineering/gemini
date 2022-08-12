#! /bin/bash
#
# script name: discountensusdskim.bash
# script author: munair simpson
# script created: 20220804
# script purpose: bid and ask on ENS using a fixed amount of ENS (the base currency).

# LONG on ENS and accumulating gains in USD:
# Parameter 0 is the pair.
# Parameter 1 is the size (of the order in terms of the base currency, thus 100 is 100 ENS).
# Parameter 2 is the discount (0.003 is a 0.3% discount on the market price).
# Parameter 3 is the premium (0.007 is a 0.7% premium on the purchase price).

# Bullish Market Trend: make the premium more than the discount.
# Bearish Market Trend: make the discount more than the premium.

# Production
# python3 ../discountfrontrunningskim.py ENSUSD 20 0.0376 0.0378

# Little Dipper Testing
# python3 ../discountfrontrunningskim.py ENSUSD 1 0.0037 0.0037

# Big Dipper Testing
# python3 ../discountfrontrunningskim.py ENSUSD 1 0.076 0.078

# Gemini's API Transaction Fee
# Presently: 20 basis points (or '0.002').
# Premium Impact: Always add 0.002 to the premium desired (in order to offset the fee for selling).
# Discount Impact: Always subtract 0.002 from the discount desired (in order to offset the fee for buying).

while [[ True ]]; do
  python3 ../discountfrontrunningskim.py ENSUSD 60 0.0076 0.01378
done
