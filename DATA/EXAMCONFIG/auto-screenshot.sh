#!/bin/bash

#this script is taking a screenshot every n second n times (12 times every 5th minute takes 1 hour)
#the EXAM mode puts this script into the autstart folder before it starts the exam desktop 
#it also removes the script but in case something went wrong the script is per default only taking 48 images 

SCREENSHOTINTERVALL=300;   #seconds    (every 5th minute)
LOOPS=48;           #repeat - but not indefinitely..  4h



USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"
MOUNTPOINT="${HOME}SHARE/.screenshots/"
SHARE="${HOME}SHARE/"

# make sure this is loaded on plasma start
exec sudo -u ${USER} -H qdbus org.kde.kglobalaccel /kglobalaccel blockGlobalShortcuts true


shoot(){
    if [ -d $MOUNTPOINT ]
    then
        for (( c=1; c<=$LOOPS; c++ ))
        do
            import -window root ${MOUNTPOINT}$(date -d "today" +"%d-%m-%Y_%H-%M-%S").jpg & sleep $SCREENSHOTINTERVALL;
        done
    else
        mkdir -p $MOUNTPOINT
        sleep 1
        shoot
    fi
}
shoot





