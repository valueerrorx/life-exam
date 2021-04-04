#!/bin/bash

RUNNING="0"
NOTRUNNINGCOUNT=0
RUNNINGCOUNT=0



check(){
    if [[ $RUNNINGCOUNT > "8" ]] 
    then 
        echo "Job done"
        exit 0
    fi
    


    RUNNING=$(ps caux|grep kwin_x11| wc -l)
    if [[ $RUNNING = "0" ]]
    then
        echo "kwin_x11 is not running! Starting KWIN"
        kwin_x11 --replace &
        
        $NOTRUNNINGCOUNT = $NOTRUNNINGCOUNT+1
        sleep 2
        echo $NOTRUNNINGCOUNT
        
        check
    else
        echo "kwin_x11 is running!"
        RUNNINGCOUNT=$(( $RUNNINGCOUNT + 1 ))
        sleep 2
        echo $RUNNINGCOUNT
        
        check
    fi
}


check
