#! /bin/bash
#
# script name: btcusdspreadkillingask.bash
# script author: munair simpson
# script created: 20210303
# script purpose: very competitive ask for USD

# Parameter 0 is the pair.
# Parameter 1 is the order size in terms of the base currency (0.07765 is 0.07765 BTC).
python3 ../spreadkillingask.py BTCUSD 0.57066604 && echo success!
