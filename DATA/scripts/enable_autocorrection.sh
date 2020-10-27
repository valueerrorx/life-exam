#!/bin/bash

# dont forget the trailing slash - otherwise shell will think its a file
# logname seems to always deliver the current xsession user - no matter if you are using SUDO
USER=$(logname)   
HOME="/home/${USER}/"
# absolute path in order to be accessible from all script locations
BACKUPDIR="${HOME}.life/unlockedbackup/"

cp -a ${BACKUPDIR}acor*  ${HOME}.config/libreoffice/4/user/autocorr/   
sudo cp -a ${BACKUPDIR}acor* /usr/lib/libreoffice/share/autocorr/ 
