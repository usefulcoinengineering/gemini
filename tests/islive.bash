#! /bin/bash
#
# script name: islive.bash
# script author: munair simpson
# script created: 20220816
# script purpose: wrapper for islive.py

# Check the order number specified is active on the orderbook (i.e. has remaining size and has not been canceled) using Gemini's REST API:
# Parameter 0 is the order number.

# Execution:
# python3 ../islive.py 136457975606

order="136457975606"

read -p "type a replacement value or press enter to continue with default argument [$order]: " order && order=${order:-136457975606}

python3 ../islive.py $order