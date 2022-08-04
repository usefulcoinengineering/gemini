#! /bin/bash
#
# script name: discountzrxusdskim.bash
# script author: munair simpson
# script created: 20210306
# script purpose: bid and ask on ZRX using a fixed amount of ZRX (the base currency).

# LONG on ZRX and accumulating gains in USD:
# Parameter 0 is the pair.
# Parameter 1 is the size (of the order in terms of the base currency, thus 1500 is 1500 ZRX).
# Parameter 2 is the discount (0.003 is a 0.3% discount on the market price).
# Parameter 3 is the premium (0.007 is a 0.7% premium on the purchase price).
while [[ True ]]; do
  python3 ../discountfrontrunningskim.py ZRXUSD 1500 0.0376 0.0376
done
