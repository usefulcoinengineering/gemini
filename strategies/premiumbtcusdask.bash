#! /bin/bash
#
# script name: discountbtcusdask.bash
# script author: munair simpson
# script created: 20210303
# script purpose: (base currency) ask for USD (providing BTC)

# SHORT on BTC and LONG on USD, where:
# Parameter 0 is the pair.
# Parameter 1 is the order size in terms of the base currency (0.07765 is 0.07765 BTC).
# Parameter 2 is the premium (0.02 is a 2% premium).
python3 ../discountfrontrunningask.py BTCUSD 0.07765 0.01 && echo success!
