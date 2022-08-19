#! /bin/bash
#
# script name: sendmessage.bash
# script author: munair simpson
# script created: 20220819
# script purpose: wrapper for sendmessage.py

# Send message specified.
# Parameter 0 is the message.

# Execution:
# python3 ../sendmessage.py "Sending a test message from a BASH script."

message="Sending a test message from a BASH script that is a wrapper around a Python script (sendmessage.py)."

read -p "type a replacement value or press enter to continue with default argument [$message]: " message
message=${message:-"Sending a test message from a BASH script that is a wrapper around a Python script (sendmessage.py)."}

python3 ../sendmessage.py $message