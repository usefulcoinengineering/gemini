#! /bin/bash
#
# script name: minimumask.bash
# script author: munair simpson
# script created: 20220811
# script purpose: wrapper for minimumask.py

# Retrieve public market data on the lowest ask in the orderbook using Gemini's REST API:
# Parameter 0 is the pair.

# Execution:
# python3 ../minimumask.py ENSUSD

pair="ETHUSD"

read -p "type a replacement value or press enter to continue with default argument [$pair]: " pair && pair=${pair:-ETHUSD}

python3 ../minimumask.py $pair