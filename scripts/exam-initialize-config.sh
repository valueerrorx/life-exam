#!/bin/bash
# last updated: 26.01.2017

# SERVER FILE #

CONFIGDIR="./FILESSERVER/EXAMCONFIG"
BACKUPDIR="./FILESSERVER/EXAMCONFIG/unlockedbackup"
LOCKDOWNDIR="./FILESSERVER/EXAMCONFIG/lockdown"

  


if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox 'You need root privileges - Stopping program' --title 'Starting Exam Config' --caption "Starting Exam Config"
    exit 1
fi
if [ -f "/etc/kde5rc" ];then
    kdialog  --msgbox 'Desktop is locked - Stopping program' --title 'Starting Exam Config' --caption "Starting Exam Config"
    exit 1
fi
if [ -f "${CONFIGDIR}/exam" ];then
    kdialog  --msgbox 'Already running exam - Stopping program' --title 'Starting Exam Config' --caption "Starting Exam Config"
    exit 1
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
    cp -Ra  /home/student/.kde/share/config/* ${BACKUPDIR}/kde.config/
    cp -Ra  /home/student/.config/* ${BACKUPDIR}/home.config/
    # backup current desktop config
    qdbus $progress Set "" value 2
    qdbus $progress setLabelText "Sichere programmspezifische Konfigurationsdateien.... "
    cp -Ra  /home/student/.local/* ${BACKUPDIR}/home.local/
  







#load minimal plasma config with stop exam icon, libreoffice, dolphin, geogebra, kcalc, 
qdbus $progress Set "" value 3
qdbus $progress setLabelText "Lade Desktop Konfiguration für Prüfungsumgebung...."

    #----------------------------------------------------------------------------------#
    # LOAD DEFAULT EXAM CONFIG - WITHOUT SYSTEM LOCK FILES (shortcuts, xorg, kde5rc)   #
    #----------------------------------------------------------------------------------#
    cp -a ${LOCKDOWNDIR}/plasma-EXAM    /home/student/.config/plasma-org.kde.plasma.desktop-appletsrc
    cp -a ${LOCKDOWNDIR}/kwinrc-EXAM /home/student/.config/kwinrc
    cp -a ${LOCKDOWNDIR}/Office.conf-EXAM /home/student/.config/Kingsoft/Office.conf
    cp -a ${LOCKDOWNDIR}/registrymodifications.xcu-EXAM /home/student/.config/libreoffice/4/user/registrymodifications.xcu
    cp -a ${LOCKDOWNDIR}/user-places.xbel-EXAM /home/student/.local/share/user-places.xbel




#mount ABGABE to /home/student/Abgabe
qdbus $progress Set "" value 4
qdbus $progress setLabelText "Mounte Austauschpartition in das Verzeichnis ABGABE...."


    #---------------------------------#
    # MOUNT ABGABE                    #
    #---------------------------------#
    mkdir /home/student/ABGABE
    sudo mount -o umask=002,uid=1000,gid=1000 /dev/disk/by-label/ABGABE /home/student/ABGABE




qdbus $progress Set "" value 5
qdbus $progress setLabelText "Prüfungsumgebung vorbereitet..."
sleep 1


    #---------------------------------#
    # CREATE SAVE CONFIG LINK         #
    #---------------------------------#
    sudo cp "Speichere Prüfungsumgebung.desktop" /home/student/ABGABE


    #---------------------------------#
    # CREATE EXAM LOCK FILE           #
    #---------------------------------#
    touch ${CONFIGDIR}/exam





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
    sudo killall Xorg



