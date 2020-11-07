#! /bin/bash
#
# script name: discountethusdquotabid.bash
# script author: munair simpson
# script created: 20201022
# script purpose: bid on ETH using USD on quota

# LONG on ETH and SHORT on USD, where:
# LONG on ETH and SHORT on USD, where:
# Parameter 0 is the pair.
# Parameter 1 is the budget (100 is 100 USD).
# Parameter 2 is the discount (0.02 is a 2% discount).
python3 ../discountquotafrontrunningbid.py ETHUSD 17000.02 0.002 && echo success!
