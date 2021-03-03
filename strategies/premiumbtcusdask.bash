#! /bin/bash
#
# script name: premiumbtcusdask.bash
# script author: munair simpson
# script created: 20210303
# script purpose: (base currency) ask for USD (providing BTC)

# SHORT on BTC and LONG on USD, where:
# Parameter 0 is the pair.
# Parameter 1 is the order size in terms of the base currency (0.07765 is 0.07765 BTC).
# Parameter 2 is the premium (0.03 is a 3% premium).
python3 ../premiumfrontrunningask.py BTCUSD 0.00032468 0.03 && echo success!
