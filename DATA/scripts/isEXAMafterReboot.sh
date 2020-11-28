#!/bin/bash
# last updated: 16.01.2020
# is there a running EXAM after Client Reboot
# maybe the the EXAM wasn't shutdown properly
#
# place a link in .profile of the student
#
# CLIENT FILE


USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"
EXAMLOCKFILE="${HOME}.life/EXAM/exam.lock"
FIRSTSTARTFILE="${HOME}.life/EXAM/startid.lock"

#--------------------------------#
# Check running exam             #
#--------------------------------#

if [ -f "$EXAMLOCKFILE" ];then
    # at the first startup we have a Startup Lock File too > we dont stop EXAM
    if [ -f "$FIRSTSTARTFILE" ];then
        # read first line
        echo "First Startup of LIFE EXAM, we do nothing"
        # Exam has startet, remove first Startup File
        rm $FIRSTSTARTFILE
    else
        # kdialog  --msgbox 'Found an running Exam - stopping it right now!' --title 'Exam is running'
        sleep 2
        # reading Config Data from lock File
        CLEAN=$(sed -n '2p' < $EXAMLOCKFILE)
        SPELL=$(sed -n '4p' < $EXAMLOCKFILE)
        if [[ "$SPELL" == "None" ]]; then
            SPELL=0
        fi
        # parameters cleanup_abgabe spellcheck skip dialogs=1
        echo $CLEAN
        echo $SPELL
        
        sudo ${HOME}.life/EXAM/scripts/stopexam.sh $CLEAN $SPELL 1
        exit 0
    fi
fi
