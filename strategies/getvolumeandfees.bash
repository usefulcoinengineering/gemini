#! /bin/bash
#
# script name: getvolumeandfees.bash
# script author: munair simpson
# script created: 20210307
# script purpose: get 30-day notional volume and the fee charged to makers using the Gemini API.

python3 ../notionalvolume.py api_maker_fee_bps
python3 ../notionalvolume.py notional_30d_volume
