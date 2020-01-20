#!/bin/bash
# last updated: 16.01.2020
# is there a running EXAM after CLient Reboot
# maybe the the EXAM wasnt shutdown properly
#
# place a link in .profile of the student
#
# CLIENT FILE


USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"
EXAMLOCKFILE="${HOME}.life/EXAM/exam.lock"

#--------------------------------#
# Check if root and running exam #
#--------------------------------#

if [ -f "$EXAMLOCKFILE" ];then
    kdialog  --msgbox 'Found an Exam - stopping it right now!' --title 'Exam is running'
    sleep 2
    ${HOME}.life/EXAM/scripts/stopexam.sh
    exit 0
fi
