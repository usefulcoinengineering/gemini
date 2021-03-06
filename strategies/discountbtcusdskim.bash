#! /bin/bash
#
# script name: discountbtcusdskim.bash
# script author: munair simpson
# script created: 20210305
# script purpose: bid and ask on BTC using a fixed amount of BTC (the base currency).

# LONG on BTC and accumulating gains in USD:
# Parameter 0 is the pair.
# Parameter 1 is the size (of the order in terms of the base currency, thus 100 is 100 BTC).
# Parameter 2 is the discount (0.003 is a 0.3% discount on the market price).
# Parameter 3 is the premium (0.007 is a 0.7% premium on the purchase price).
while [[ True ]]; do
  python3 ../discountfrontrunningskim.py BTCUSD 0.01376 0.003 0.0076
done
