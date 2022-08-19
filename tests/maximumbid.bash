#! /bin/bash
#
# script name: maximumbid.bash
# script author: munair simpson
# script created: 20220811
# script purpose: wrapper for maximumbid.py

# Retrieve public market data on the highest bid in the pairbook using Gemini's REST API:
# Parameter 0 is the pair.

# Execution:
# python3 ../maximumbid.py ENSUSD

pair="ETHUSD"

read -p "type a replacement value or press enter to continue with default argument [$pair]: " pair && pair=${pair:-136457975606}

python3 ../maximumbid.py $pair