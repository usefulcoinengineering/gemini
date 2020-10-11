#! /bin/bash
#
# script name: skimyfiusd.bash
# script author: munair simpson
# script created: 20201010
# script purpose: bid and ask on YFI using USD on quota

# LONG on YFI and accumulating YFI:
while [[ True ]]; do
  python3 ../discountquotabid.py YFIUSD 137.60 0.02 || break
  python3 ../discountquotaask.py YFIUSD 137.60 0.02 || break
done
