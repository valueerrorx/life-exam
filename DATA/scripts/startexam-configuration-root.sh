#!/bin/bash
# last updated: 26.01.2017

# SERVER FILE #

# dont forget the trailing slash - otherwise shell will think its a file


USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"

EXAMLOCKFILE="${HOME}.life/EXAM/exam.lock"
LOCKDOWNDIR="${HOME}.life/EXAM/EXAMCONFIG/lockdown/"
BACKUPDIR="${HOME}.life/EXAM/unlocked-backup/"
SCRIPTDIR="${HOME}.life/EXAM/scripts/"
ABGABE="${HOME}ABGABE/"


#--------------------------------#
# Check if root and running exam #
#--------------------------------#
if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox 'You need root privileges - Stopping program' --title 'Starting Exam Config' --caption "Starting Exam Config"
    exit 1
fi
if [ -f "/etc/kde5rc" ];then
    kdialog  --msgbox 'Desktop is locked - Stopping program' --title 'Starting Exam Config' --caption "Starting Exam Config"
    exit 1
fi
if [ -f "$EXAMLOCKFILE" ];then
    kdialog  --msgbox 'Already running exam - Stopping program' --title 'Starting Exam Config' --caption "Starting Exam Config"
    exit 1
fi
if [ ! -d "$BACKUPDIR" ];then
    mkdir $BACKUPDIR
fi
if [ ! -d "${BACKUPDIR}kde.config/" ];then
    mkdir ${BACKUPDIR}kde.config/
    mkdir ${BACKUPDIR}home.config/
    mkdir ${BACKUPDIR}home.local/
fi





## start progress with a lot of spaces (defines the width of the window - using geometry will move the window out of the center)
progress=$(kdialog --title "EXAM Config" --caption "EXAM Config" --progressbar "Lade Prüfungsumgebung                                                               "); 
qdbus $progress Set "" maximum 6
sleep 0.5

    #---------------------------------#
    # BACKUP CURRENT DESKTOP CONFIG   #
    #---------------------------------#
    qdbus $progress Set "" value 1
    qdbus $progress setLabelText "Sichere aktuelle Desktop Konfiguration.... "
    qdbus $progress Set "" value 2
    qdbus $progress setLabelText "Sichere programmspezifische Konfigurationsdateien.... "
    
    cp -Ra  ${HOME}.kde/share/config/* ${BACKUPDIR}kde.config/
    cp -Ra  ${HOME}.config/* ${BACKUPDIR}home.config/
    cp -Ra  ${HOME}.local/* ${BACKUPDIR}home.local/
  







#load minimal plasma config with stop exam icon, libreoffice, dolphin, geogebra, kcalc, 
qdbus $progress Set "" value 3
qdbus $progress setLabelText "Lade Desktop Konfiguration für Prüfungsumgebung...."

    #----------------------------------------------------------------------------------#
    # LOAD DEFAULT EXAM CONFIG - WITHOUT SYSTEM LOCK FILES (shortcuts, xorg, kde5rc)   #
    #----------------------------------------------------------------------------------#
    cp -a ${LOCKDOWNDIR}plasma-EXAM    ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc
    cp -a ${LOCKDOWNDIR}kwinrc-EXAM ${HOME}.config/kwinrc
    cp -a ${LOCKDOWNDIR}Office.conf-EXAM ${HOME}.config/Kingsoft/Office.conf
    cp -a ${LOCKDOWNDIR}registrymodifications.xcu-EXAM ${HOME}.config/libreoffice/4/user/registrymodifications.xcu
    cp -a ${LOCKDOWNDIR}user-places.xbel-EXAM ${HOME}.local/share/user-places.xbel




#mount ABGABE to ${HOME}Abgabe
qdbus $progress Set "" value 4
qdbus $progress setLabelText "Mounte Austauschpartition in das Verzeichnis ABGABE...."

    #---------------------------------#
    # MOUNT ABGABE                    #
    #---------------------------------#
    mkdir $ABGABE 2> /dev/null
    sudo mount -o umask=002,uid=1000,gid=1000 /dev/disk/by-label/ABGABE $ABGABE




qdbus $progress Set "" value 5
qdbus $progress setLabelText "Prüfungsumgebung vorbereitet..."
sleep 1

    #---------------------------------#
    # CREATE SAVE CONFIG LINK         #
    #---------------------------------#
    sudo cp "${SCRIPTDIR}Speichere Prüfungsumgebung.desktop" $ABGABE


    #---------------------------------#
    # CREATE EXAM LOCK FILE           #
    #---------------------------------#
    touch $EXAMLOCKFILE





qdbus $progress Set "" value 6
qdbus $progress setLabelText "
Speichern/Beenden sie Ihre Anpassungen mit Hilfe des LIFE Helferprogrammes 'Prüfungsumgebung speichern'

Starte Prüfungsdesktop in 4 Sekunden!"
sleep 2
sleep 2
qdbus $progress close

    #---------------------------------#
    # RESTART DESKTOP TO EXAM DESKTOP #
    #---------------------------------#
  
    
   # kill running programs to allow new config to load
    pkill -f dolphin
    pkill -f google
    pkill -f firefox
    pkill -f writer
    pkill -f kwrite
    pkill -f konsole
    pkill -f geogebra

  
sudo -u ${USER} kquitapp5 plasmashell && sudo -u ${USER} kstart5 plasmashell &
sudo -u ${USER} kwin --replace &



 

