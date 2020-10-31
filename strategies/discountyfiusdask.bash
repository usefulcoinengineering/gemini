#! /bin/bash
#
# script name: discountyfiusdask.bash
# script author: munair simpson
# script created: 20201031
# script purpose: ask on YFI using USD on quota

# LONG on YFI and SHORT on USD, where:
# LONG on YFI and SHORT on USD, where:
# Parameter 0 is the pair.
# Parameter 1 is the order size in terms of the base currency (0.07765 is 0.07765 YFI).
# Parameter 2 is the discount (0.02 is a 2% discount).
python3 ../discountfrontrunningask.py YFIUSD 0.07765 0.01 && echo success!
