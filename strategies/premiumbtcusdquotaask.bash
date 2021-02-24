#! /bin/bash
#
# script name: premiumbtcusdquotaask.bash
# script author: munair simpson
# script created: 20210223
# script purpose: BTC (base) ask for USD (quote) on quota

# LONG on USD and SHORT on BTC, where:
# Parameter 0 is the pair.
# Parameter 1 is the budget (100 is 100 USD).
# Parameter 2 is the premium (0.02 is a 2% premium).
python3 ../discountquotafrontrunningask.py BTCUSD 10000 0.0178 && echo success!
