#!/bin/bash

#this script is taking a screenshot every n second n times (12 times every 5th minute takes 1 hour)
#the EXAM mode puts this script into the autstart folder before it starts the exam desktop 
#it also removes the script but in case something went wrong the script is per default only taking 48 images 

SCREENSHOTINTERVALL=300;   #seconds    (every 5th minute)
LOOPS=48;           #repeat


MOUNTPOINT="/home/student/ABGABE/.screenshots"
    


shoot(){
    if [ -d $MOUNTPOINT ]
    then
        for (( c=1; c<=$LOOPS; c++ ))
        do
            scrot -b -d 0 "%Y-%m-%d-%H-%M-%S.jpg" -e 'mv $f /home/student/ABGABE/.screenshots' & sleep $SCREENSHOTINTERVALL;
        done
    else
        mkdir -p $MOUNTPOINT
        sleep 1
        shoot
    fi
}
shoot





