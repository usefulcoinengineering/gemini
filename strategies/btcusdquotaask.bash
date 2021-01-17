#! /bin/bash
#
# script name: btcusdquotaask.bash
# script author: munair simpson
# script created: 20210117
# script purpose: ask on BTC using USD on quota

# LONG on USD and SHORT on BTC, where:
# Parameter 0 is the pair.
# Parameter 1 is the budget (1000 is 1000 USD).
# Parameter 2 is the price (450 is 450 USD).
python3 ../quotaask.py BTCUSD 10000 36780 && echo success!
