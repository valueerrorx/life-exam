#!/bin/bash
# last updated: 26.01.2017
# restores default desktop configuration after saving (or not saving) exam konfiguration

# SERVER FILE #



# dont forget the trailing slash - otherwise shell will think its a file

BACKUPDIR="~/.life/EXAM/unlocked-backup/" #absolute path in order to be accessible from all script locations
LOCKDOWNDIR="~/.life/EXAM/EXAMCONFIG/lockdown/"
EXAMLOCKFILE="~/.life/EXAM/exam.lock"

  



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
qdbus $progress Set "" maximum 6
sleep 0.5




if [ "$answer" = 0 ]; then
    qdbus $progress Set "" value 1
    qdbus $progress setLabelText "Sichere aktuelle Desktop Konfiguration als Prüfungsumgebung.... "
    sleep 1
    #------------------------------------------------#
    # SAVE CURRENT EXAM CONFIG FILES TO LOCKDOWNDIR  #
    #------------------------------------------------#
    cp -a /home/student/.config/plasma-org.kde.plasma.desktop-appletsrc ${LOCKDOWNDIR}plasma-EXAM  
    cp -a /home/student/.local/share/user-places.xbel ${LOCKDOWNDIR}user-places.xbel-EXAM
   # cp -a /home/student/.config/kglobalshortcutsrc ${LOCKDOWNDIR}/kglobalshortcutsrc-EXAM   #always use the "noshortcuts" file - don't allow configuring for now
    cp -a /home/student/.config/Kingsoft/Office.conf ${LOCKDOWNDIR}Office.conf-EXAM
    cp -a /home/student/.config/libreoffice/4/user/registrymodifications.xcu ${LOCKDOWNDIR}registrymodifications.xcu-EXAM
    cp -a /home/student/.config/kwinrc ${LOCKDOWNDIR}kwinrc-EXAM

    
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
sudo rm "/home/student/ABGABE/Speichere Prüfungsumgebung.desktop"
sudo rm $EXAMLOCKFILE   #remove this file otherwise LIFE will think exam (config) is still running

#copy backup over original
qdbus $progress Set "" value 2
qdbus $progress setLabelText "Stelle Standard Desktop Konfiguration wieder her.... "
cp -Ra ${BACKUPDIR}kde.config/* /home/student/.kde/share/config/
cp -Ra ${BACKUPDIR}home.config/* /home/student/.config/

#copy backup over original
qdbus $progress Set "" value 3
qdbus $progress setLabelText "Stelle Standard Programm Konfiguration wieder her.... "
cp -Ra ${BACKUPDIR}home.local/* /home/student/.local/


#remove icon cache - otherwise some changes will not be visible
qdbus $progress Set "" value 4
qdbus $progress setLabelText "Entferne Icon Cache.... "
sleep 0.5
sudo rm /usr/share/icons/hicolor/icon-theme.cache > /dev/null 2>&1  #hide errors
sudo rm /var/tmp/kdecache-student/plasma_theme_default.kcache > /dev/null 2>&1  #hide errors
sudo rm /var/tmp/kdecache-student/icon-cache.kcache > /dev/null 2>&1  #hide errors
sudo rm -r /home/student/.cache > /dev/null 2>&1  #hide errors

#unmount ABGABE
qdbus $progress Set "" value 5
qdbus $progress setLabelText "Gebe Ordner ABGABE wieder frei.... "
sudo umount -l /home/student/ABGABE
sleep 2
rmdir /home/student/ABGABE



qdbus $progress Set "" value 6
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
sudo killall Xorg
    



















