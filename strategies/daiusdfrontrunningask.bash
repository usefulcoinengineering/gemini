#! /bin/bash
#
# script name: daiusdspreadkillingask.bash
# script author: munair simpson
# script created: 20201105
# script purpose: very competitive ask for USD

# Parameter 0 is the pair.
# Parameter 1 is the order size in terms of the base currency (0.1 is 0.1 DAI).
python3 ../frontrunningask.py DAIUSD 19834.79999604 && echo success!
