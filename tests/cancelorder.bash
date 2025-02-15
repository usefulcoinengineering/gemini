#! /bin/bash
#
# script name: cancelorder.bash
# script author: munair simpson
# script created: 20220816
# script purpose: wrapper for cancelorder.py

# Cancel order number specified.
# Parameter 0 is the order number.

# Execution:
# python3 ../cancelorder.py 136457975606

order="136457975606"

read -p "type a replacement value or press enter to continue with default argument [$order]: " order && order=${order:-136457975606}

python3 ../cancelorder.py $order