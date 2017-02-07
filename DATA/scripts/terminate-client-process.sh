#!/bin/bash
# this file grabs the twistd client pid from the pidfile and kills the process

USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"
CLIENTPIDFILE="${HOME}.life/EXAM/client.pid"

if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox 'You need root privileges - Stopping program' --title 'Starting Exam Config' --caption "Starting Exam Config"
    exit 1
fi


PID=$(sudo cat ${CLIENTPIDFILE})
sudo kill -9 $PID
