#! /bin/bash
#
# script name: btcusdspreadkillingask.bash
# script author: munair simpson
# script created: 20210303
# script purpose: very competitive ask for USD

# Parameter 0 is the pair.
# Parameter 1 is the order size in terms of the base currency (0.1 is 0.1 BTC).
python3 ../frontrunningask.py BTCUSD 19834.79999 && echo success!
