#!/bin/bash

KWINRUNNING="0"
PLASMARUNNING="0"
RUNNINGCOUNT=0


check(){
#     if [[ $RUNNINGCOUNT > "8" ]] 
#     then 
#         echo "Job done"
#         exit 0
#     fi
#   
 
    SLEEP=2
 
    KWINRUNNING=$(ps caux|grep kwin_x11| wc -l)
    PLASMARUNNING=$(ps caux|grep plasmashell| wc -l)
    
    if [[ $KWINRUNNING = "0" ]]
    then
        echo "kwin_x11 is not running! Starting KWIN"
        kstart5 kwin_x11&
    else
        echo "kwin_x11 is running!"
        SLEEP=10
    fi
    
    
    if [[ $PLASMARUNNING = "0" ]]
    then
        echo "Plasmashell is not running! Starting Plasmashell"
        kstart5 plasmashell 
    else
        echo "Plasmashell is running!"
        SLEEP=10
    fi
    
    sleep $SLEEP
    
    check
}


check
