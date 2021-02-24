#! /bin/bash
#
# script name: skimbtcusd.bash
# script author: munair simpson
# script created: 20201010
# script purpose: bid and ask on BTC using USD on quota

# LONG on BTC and accumulating BTC:
# Parameter 0 is the pair.
# Parameter 1 is the budget (100 is 100 USD).
# Parameter 2 is the discount (0.02 is a 2% discount).
while [[ True ]]; do
  python3 ../quotafrontrunningskim.py BTCUSD 13789 0.003 0.003
done
