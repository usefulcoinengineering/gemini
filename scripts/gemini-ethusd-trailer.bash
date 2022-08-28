#!/usr/bin/bash
# 
# script name: gemini-ethusd-trailer.bash
# script author: munair simpson
# script created: 20220827
# script purpose: start or stop a Gemini ETHUSD trailer bot from [~/bots]
# script argument: the action desired [start/stop]

if [ "$#" != "1" ]; then

    # step 1: explain error
    echo "You should have provided either 'start' or 'stop' as an argument. "
    echo "Not to worry... Please respond to the questions that follow. "

    # step 2: ask about checking for existing detached processes
    read -p "Would you like to check for the presence of running bots? [yes]: " pingerprompt
    pingerprompt=${pingerprompt:-"yes"}
    if [ $pingerprompt == "yes "]; then 
        ps auwx | grep -e "bash [bf]" -e "python3 \." | grep -v "$0" && echo "there are active bots running. "
        if [ $? == "1" ]; then 
            echo "no active bots found... "
        else

            # step 3: ask how to handle detached processes since they must exist
            read -p "Do you want to kill these running bots? [yes]: " killerprompt
            killerprompt=${killerprompt:-"yes"}
            if [ $pingerprompt == "yes "]; then action="stop" ; fi        
        fi
    fi

    # step 4: ask whether to bootstrap the bot
    read -p "Do you want to start/boot up a bot? [yes]: " booterprompt
    booterprompt=${booterprompt:-"yes"}
    if [ $pingerprompt == "yes "]; then action="start" ; fi   
else
    action=$1
fi

# step 5: verify
ps auwx | grep -e "bash [bf]" -e "python3 \." | \
grep -v "$0" && echo "There are active bots running. " && \
read "Proceed? [no]" verifyprompt && verifyprompt=${verifyprompt-"no"} && \
if [ $verifyprompt == "no" ]; then exit 1 ; fi

# step 6: start or stop bot
if [ $action == "stop" ]; then kill -s KILL $(ps auwx | grep -E 'bash [bf]|python3 \.' | awk '{print $2}') ; fi
if [ $action == "start" ]; then cd gemini/strategies/ && git pull && nohup bash frontrunningethusdtrailingstop.bash ; fi

exit 0