#! /bin/bash
#
# script name: discountbtcusdquotaskim.bash
# script author: munair simpson
# script created: 20210225
# script purpose: bid and ask on BTC using USD on quota

# LONG on BTC and accumulating gains in BTC:
# Parameter 0 is the pair.
# Parameter 1 is the budget (100 is 100 USD).
# Parameter 2 is the discount (0.003 is a 0.3% discount on the market price).
# Parameter 3 is the premium (0.007 is a 0.7% premium on the purchase price).
while [[ True ]]; do
  python3 ../discountquotafrontrunningskim.py BTCUSD 1378 0.003 0.0076
done
