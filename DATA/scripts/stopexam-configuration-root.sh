#!/bin/bash
# last updated: 26.01.2017
# restores default desktop configuration after saving (or not saving) exam konfiguration

# SERVER FILE #



# dont forget the trailing slash - otherwise shell will think its a file


USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"

BACKUPDIR="${HOME}.life/EXAM/EXAMCONFIG/unlocked-backup/" #absolute path in order to be accessible from all script locations
LOCKDOWNDIR="${HOME}.life/EXAM/EXAMCONFIG/lockdown/"
EXAMLOCKFILE="${HOME}.life/EXAM/exam.lock"
ABGABE="${HOME}ABGABE/"
  



if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox 'You need root privileges - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    exit 1
fi
if [ -f "/etc/kde5rc" ];then
    kdialog  --msgbox 'Desktop is locked - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    sleep 2
    exit 1
fi
if ! [ -f "$EXAMLOCKFILE" ];then
    kdialog  --msgbox 'Not running exam - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    sleep 2
    exit 0
fi





kdialog --yesnocancel "Die Anpassung des Prüfungsdesktops wird beendet.                                                \n\nBitte achten Sie darauf, dass ein Link zum Programm 'Stoppe Prüfungsumgebung' am Desktop erreichbar sein muss.\n\nWollen sie die Änderungen speichern?" --title "EXAM" --caption "EXAM";
answer="$?";









#---------------------------------------------##---------------------------------------------#
# wenn normal modus - speicher die veränderte desktop datei als plasma-EXAM und stell den normalen desktop wieder her
#---------------------------------------------##---------------------------------------------#


## start progress with a lot of spaces (defines the width of the window - using geometry will move the window out of the center)
progress=$(kdialog --progressbar "Beende Prüfungsumgebung                                                               ");
qdbus $progress Set "" maximum 5
sleep 0.5




if [ "$answer" = 0 ]; then
    qdbus $progress Set "" value 1
    qdbus $progress setLabelText "Sichere aktuelle Desktop Konfiguration als Prüfungsumgebung.... "
    sleep 1
    #------------------------------------------------#
    # SAVE CURRENT EXAM CONFIG FILES TO LOCKDOWNDIR  #
    #------------------------------------------------#
    cp -a ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc ${LOCKDOWNDIR}plasma-EXAM  
    cp -a ${HOME}.local/share/user-places.xbel ${LOCKDOWNDIR}user-places.xbel-EXAM
   # cp -a ${HOME}.config/kglobalshortcutsrc ${LOCKDOWNDIR}/kglobalshortcutsrc-EXAM   #always use the "noshortcuts" file - don't allow configuring for now
    cp -a ${HOME}.config/Kingsoft/Office.conf ${LOCKDOWNDIR}Office.conf-EXAM
    cp -a ${HOME}.config/libreoffice/4/user/registrymodifications.xcu ${LOCKDOWNDIR}registrymodifications.xcu-EXAM
    cp -a ${HOME}.config/kwinrc ${LOCKDOWNDIR}kwinrc-EXAM

    
    #------------------------------------------------#
    #   also save other files ????                   #
    #------------------------------------------------#

elif [ "$answer" = 1 ]; then
    #------------------------------------------------#
    # CONTINUE WITHOUT SAVING                        #
    #------------------------------------------------#
    sleep 0
elif [ "$answer" = 2 ]; then
    exit 1
else
    exit 1
fi;


#remove some files
sudo rm "${ABGABE}Speichere Prüfungsumgebung.desktop"
sudo rm $EXAMLOCKFILE   #remove this file otherwise LIFE will think exam (config) is still running

#copy backup over original
qdbus $progress Set "" value 2
qdbus $progress setLabelText "Stelle Standard Desktop Konfiguration wieder her.... "

cp -Ra ${BACKUPDIR}kde.config/* ${HOME}.kde/share/config/
cp -Ra ${BACKUPDIR}home.config/* ${HOME}.config/
cp -Ra ${BACKUPDIR}home.local/* ${HOME}.local/


#remove icon cache - otherwise some changes will not be visible
qdbus $progress Set "" value 3
qdbus $progress setLabelText "Entferne Icon Cache.... "
sleep 0.5
sudo rm /usr/share/icons/hicolor/icon-theme.cache > /dev/null 2>&1  #hide errors
sudo rm /var/tmp/kdecache-${USER}/plasma_theme_default.kcache > /dev/null 2>&1  #hide errors
sudo rm /var/tmp/kdecache-${USER}/icon-cache.kcache > /dev/null 2>&1  #hide errors
sudo rm -r ${HOME}.cache > /dev/null 2>&1  #hide errors

#unmount ABGABE
qdbus $progress Set "" value 4
qdbus $progress setLabelText "Gebe Ordner ABGABE wieder frei.... "
sudo umount -l $ABGABE
sleep 2
rmdir $ABGABE



qdbus $progress Set "" value 5
if [ "$answer" = 0 ]; then
    qdbus $progress setLabelText "Prüfungsumgebung gespeichert....  
Starte Desktop neu!"
else
    qdbus $progress setLabelText "Prüfungsumgebung nicht gespeichert....  
Starte Desktop neu!"
fi

sleep 4
qdbus $progress close


##  restart desktop !!

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



















