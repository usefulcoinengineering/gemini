#! /bin/bash
#
# script name: stoplimitask.bash
# script author: munair simpson
# script created: 20220815
# script purpose: wrapper for stoplimitask.py

# Submit a "stop-limit" sell order the orderbook using Gemini's REST API:
# Parameter 0 is the pair.
# Parameter 1 is the size.
# Parameter 2 is the stop.
# Parameter 3 is the sell.

# Execution:
# python3 ../stoplimitask.py ETHUSD

python3 ../stoplimitask.py ETHUSD 0.001 1896.43 1976.43