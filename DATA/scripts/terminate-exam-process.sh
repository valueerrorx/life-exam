#!/bin/bash
# this file grabs the twistd client pid from the pidfile and kills the process

#logname seems to always deliver the current xsession user - no matter if you are using SUDO
USER=$(logname)
HOME="/home/${USER}/"

if [[ "$1" == "client" ]]
then
    PIDFILE="${HOME}.life/EXAM/client.pid"
else
    PIDFILE="${HOME}.life/EXAM/server.pid"
fi


if [ -f $PIDFILE ];
then
    if [ "$(id -u)" != "0" ]; then
        kdialog  --msgbox "You need root privileges - can't delete Exam-Client.pid" --title 'Starting Exam Config' 
        exit 1
    fi

    PID=$(sudo cat ${PIDFILE})
    echo "terminating old process with pid $PID"
    sudo kill -9 $PID
fi
