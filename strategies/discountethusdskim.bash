#! /bin/bash
#
# script name: discountethusdskim.bash
# script author: munair simpson
# script created: 20220808
# script purpose: bid and ask on ETH using a fixed amount of ETH (the base currency).
# strategy outline: (repeatedly) purchase a fixed amount of ETH "at a discount" and sell it when the price rises.
# strategy note: the discount is super important. without that discount repeatedly buying results in a loss when you add fees.

# LONG on ETH and accumulating gains in USD:
# Parameter 0 is the pair.
# Parameter 1 is the size (of the order in terms of the base currency, thus 100 is 100 ETH).
# Parameter 2 is the discount (0.003 is a 0.3% discount on the market price).
# Parameter 3 is the premium (0.007 is a 0.7% premium on the purchase price).

# Production
# python3 ../discountfrontrunningskim.py ETHUSD 20 0.0376 0.0378

# Little Dipper Testing
# python3 ../discountfrontrunningskim.py ETHUSD 1 0.0037 0.0037

# Big Dipper Testing
# python3 ../discountfrontrunningskim.py ETHUSD 1 0.076 0.078

while [[ True ]]; do
  python3 ../discountfrontrunningskim.py ETHUSD 0.5 0.013 0.013
done
