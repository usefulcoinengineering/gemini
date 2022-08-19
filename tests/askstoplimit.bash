#! /bin/bash
#
# script name: askstoplimit.bash
# script author: munair simpson
# script created: 20220815
# script purpose: wrapper for askstoplimit.py

# Submit a "stop-limit" sell order the orderbook using Gemini's REST API:
# Parameter 0 is the pair.
# Parameter 1 is the size.
# Parameter 2 is the stop.
# Parameter 3 is the sell.

# Execution:
# python3 ../askstoplimit.py ETHUSD 0.001 0.0050 0.0100

# Define default values.
pair="ETHUSD"
size="0.0001"
stop="0.0050"
sell="0.0100"

read -p "type hostname or press enter to continue with default [$pair]: " pair && pair=${pair:-$pair}
read -p "type hostname or press enter to continue with default [$size]: " size && size=${size:-$size}
read -p "type hostname or press enter to continue with default [$stop]: " stop && stop=${stop:-$stopt}
read -p "type hostname or press enter to continue with default [$sell]: " sell && sell=${sell:-$sell}

# python3 ../askstoplimit.py $pair $size $stop $sell