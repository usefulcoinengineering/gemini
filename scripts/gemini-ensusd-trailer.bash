#!/usr/bin/bash
# 
# script name: gemini-ensusd-trailer.bash
# script author: munair simpson
# script created: 20220827
# script purpose: start or stop a Gemini ENSUSD trailer bot from [~/bots]
# script argument: the action desired [start/stop]

# ps auwx | grep -E 'bash [bf]|python3 \.' && echo "there are active bots running. "
ps auwx | grep -e "bash [bf]" -e "python3 \." | grep -vw "bash bots/gemini-ensusd-trailer.bash" && echo "there are active bots running. "

read -p "'start' or 'stop' trading bot [start]: " action
action=${action:-start}

if [ $action == "stop" ]; then kill -s KILL $(ps auwx | grep -E 'bash [bf]|python3 \.' | awk '{print $2}') ; fi
if [ $action == "start" ]; then cd gemini/strategies/ && git pull && nohup bash frontrunningensusdtrailingstop.bash ; fi