#!/bin/bash
# last updated: 13.11.2019
# loads exam desktop configuration
#
# CLIENT FILE - START EXAM
#
# dieses Skript erwartet 1 Parameter:    <delshare>  


# dont forget the trailing slash - otherwise shell will think its a file
# logname seems to always deliver the current xsession user - no matter if you are using SUDO
USER=$(logname)   
HOME="/home/${USER}/"
IPSFILE="${HOME}.life/EXAM/EXAMCONFIG/EXAM-A-IPS.DB"
CONFIGDIR="${HOME}.life/EXAM/EXAMCONFIG/"
#absolute path in order to be accessible from all script locations
BACKUPDIR="${HOME}.life/unlockedbackup/"
LOCKDOWNDIR="${HOME}.life/EXAM/EXAMCONFIG/lockdown/"
EXAMLOCKFILE="${HOME}.life/EXAM/exam.lock"
# don't remove trailing slash.. we are working with that one on folders
SHARE="${HOME}SHARE/"     
SCRIPTDIR="${HOME}.life/EXAM/scripts/"
DELSHARE=$1
SPELLCHECK=$2
RUNNINGEXAM=0

#--------------------------------#
# Check if root and running exam #
#--------------------------------#
if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox "You need root privileges - Otherwise can't sudo some stuff!" --title 'Starting Exam' 
    exit 1
fi
if [ -f "$EXAMLOCKFILE" ];then
    kdialog  --msgbox "Desktop is about to reload! \nYou need to SAVE your work BEFORE you click OK on this dialog.\n\nYou have been warned!"  --title 'Starting Exam'
    RUNNINGEXAM=1
fi
if [ -f "/etc/kde5rc" ];then
    RUNNINGEXAM=1
fi
if [ ! -d "$BACKUPDIR" ];then
    mkdir -p $BACKUPDIR
fi




#---------------------------------#   
# FUNCTIONS                       #
#---------------------------------#
    
function startFireWall(){
    sudo ${SCRIPTDIR}exam-firewall.sh start &
}


function backupCurrentConfig(){
    if [[ ( $RUNNINGEXAM = "0" ) ]]  #be careful not to store locked config instead of unlocked config here
    then
        #kde
        cp -a ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc ${BACKUPDIR}   #main desktop applets config file
        cp -a ${HOME}.config/kwinrc ${BACKUPDIR}        # windowmanager configuration
        cp -a ${HOME}.config/kglobalshortcutsrc ${BACKUPDIR}   # keyboardshortcuts
        #office
        cp -a ${HOME}.config/calligra* ${BACKUPDIR}
        #filemanagment
        cp -a ${HOME}.local/share/user-places.xbel ${BACKUPDIR}   # dolphin / filepicker places panel config
        cp -a ${HOME}.config/dolphinrc ${BACKUPDIR}    
        cp -a ${HOME}.config/user-dirs.dirs ${BACKUPDIR}  #default directories for documents music etc.
        cp -a ${HOME}.config/mimeapps.list ${BACKUPDIR}
        
        # Spell Checking 
        if [[ ( $SPELLCHECK = "0" ) ]]     #checkbox sends 0 for unchecked and 2 for checked
        then
            # disabel autocorrection if checkbox is not
            mv ${HOME}.config/libreoffice/4/user/autocorr/acor* ${BACKUPDIR}
            sudo mv /usr/lib/libreoffice/share/autocorr/acor_de* ${BACKUPDIR}
            sudo mv /usr/lib/libreoffice/share/autocorr/acor_en* ${BACKUPDIR}
            sudo mv /usr/lib/libreoffice/share/autocorr/acor_fr* ${BACKUPDIR} 
        else
            # nothing to do, means nothing to copy back
            # autocorrection was active
        fi   
        
        #chrome
        cp -a ${HOME}.config/google-chrome/Default/Preferences ${BACKUPDIR}
        sudo chown -R ${USER}:${USER} ${BACKUPDIR}  # twistd runs as root - fix ownership
    fi
}

function loadExamConfig(){
    cp -a ${LOCKDOWNDIR}plasma-EXAM ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc    #load minimal plasma config for exam 
    cp -a ${LOCKDOWNDIR}kwinrc-EXAM ${HOME}.config/kwinrc  #special windowmanager settings
    cp -a ${LOCKDOWNDIR}user-places.xbel-EXAM ${HOME}.local/share/user-places.xbel
    cp -a ${LOCKDOWNDIR}dolphinrc-EXAM ${HOME}.config/dolphinrc
    cp -a ${LOCKDOWNDIR}calligra* ${HOME}.config/
    cp -a ${LOCKDOWNDIR}user-dirs.dirs ${HOME}.config/
    cp -a ${LOCKDOWNDIR}mimeapps.list-EXAM ${HOME}.config/mimeapps.list   #dateitypen zuordnung zu programmen
    cp -a ${LOCKDOWNDIR}mimeapps.list-EXAM ${HOME}.local/share/applications/mimeapps.list
    cp -a ${LOCKDOWNDIR}Preferences ${HOME}.config/google-chrome/Default/Preferences
    
    sudo cp -a ${LOCKDOWNDIR}mimeapps.list-EXAM /usr/share/applications/mimeapps.list

    #LOCK DOWN
    sudo cp ${LOCKDOWNDIR}kde5rc-EXAM /etc/kde5rc   #this is responsible for the KIOSK settings (main lock file)
    sudo chmod 644 /etc/kde5rc     #this is necessary if the script is run form twistd plugin as root
    sudo chown -R ${USER}:${USER} ${HOME}.config/ &    # twistd runs as root - fix ownership
    sudo chown -R ${USER}:${USER} ${HOME}.local/ &
}


function mountShare(){
    mkdir $SHARE > /dev/null 2>&1
    sudo chown -R ${USER}:${USER} $SHARE   # twistd runs as root - fix permissions
    CURRENTUID=$(id -u ${USER})
    sudo mount -o umask=002,uid=${CURRENTUID},gid=${CURRENTUID} /dev/disk/by-label/SHARE $SHARE
    sudo touch $SHARE   # update timestamp on live usb devices (this is a bugfix for unix behaviour - leave it there)

    if [ -f "$EXAMLOCKFILE" ];then
        echo "already running exam"   #do nothing yet
    else
        ## only if exam is not already running delete share folder (otherwise we could delete the students work)
        if [[ ( $DELSHARE = "2" ) ]]     #checkbox sends 0 for unchecked and 2 for checked
        then
            qdbus $progress Set "" value 4
            qdbus $progress setLabelText "Bereinige SHARE...."
            sleep 0.5
            sudo rm -rf ${SHARE}*
            sudo rm -rf ${SHARE}.* 
        fi
    fi
}



function createLockFile(){
    touch $EXAMLOCKFILE
    # echo $SUBJECT > $EXAMLOCKFILE   # write subject into lockfile in order to read from it when the exam desktop should be stored
    sudo chown ${USER}:${USER} $EXAMLOCKFILE      # twistd runs as root - fix permissions
}


function runAutostartScripts(){
    cp ${CONFIGDIR}auto-screenshot.sh ${HOME}.config/autostart-scripts
    sudo chown -R ${USER}:${USER} ${HOME}.config/autostart-scripts  # twistd runs as root - fix permissions
    sudo chmod -R 755 ${HOME}.config/autostart-scripts
    nohup sudo -u ${USER} -H ${HOME}.config/autostart-scripts/auto-screenshot.sh  >/dev/null 2>&1 &
}



function blockAdditionalFeatures(){
    #students hide things in trash ? 
    rm -rf ${HOME}.local/share/Trash > /dev/null 2>&1   

    #make sure nothing is mounted in /media  
    sudo umount /media/*
    sudo umount /media/student/*
    sudo umount -l /media/*
    sudo umount -l /media/student/*
    sleep 1
        
    MOUNTED=$(df -h |grep media |wc -l)
    if [[( $MOUNTED = "1" )]]
    then
        #this should never happen .. but it did once ;-)
        sleep 0 #do nothing - we do not mess with permissions of mounted partitions
    else
        sudo chmod 600 /media/ -R   
        # this makes it impossible to mount anything in kubuntu /dolphin !!!
        # could be fatal if something is mounted there already  for examle "casper-rw" 
        #(this would immediately kill the flashdrive installation)
    fi
    
    sudo chmod 644 /sbin/agetty  # start (respawning) von virtuellen terminals auf ctrl+alt+F[1-6]  verbieten
    sudo chmod 644 /usr/bin/xterm
    sudo chmod 644 /usr/bin/konsole

    sudo systemctl stop getty@tty1.service      # laufende virtuelle terminals abschalten
    sudo systemctl stop getty@tty2.service
    sudo systemctl stop getty@tty3.service
    sudo systemctl stop getty@tty4.service
    sudo systemctl stop getty@tty5.service
    sudo systemctl stop getty@tty6.service
}


function playSound(){
    amixer -D pulse sset Master 90% > /dev/null 2>&1
    pactl set-sink-volume 0 90%
    paplay /usr/share/sounds/KDE-Sys-Question.ogg
}


function restartDesktop(){
   # FIXME (etwas brachial) man könnte auch einfach die plasma config neueinlesen - 
   # kde devs haben das bis jetzt noch nicht implementiert
    pkill -f Xorg
}


#---------------------------------#
# OPEN PROGRESSBAR DIALOG         #
#---------------------------------#
## start progress with a lot of spaces (defines the width of the window - using geometry will move the window out of the center)
progress=$(kdialog --progressbar "Starte Prüfungsumgebung                                                               "); > /dev/null
qdbus $progress Set "" maximum 8
sleep 0.2

#---------------------------------#
# INITIALIZE FIREWALL             #
#---------------------------------#
qdbus $progress Set "" value 1
qdbus $progress setLabelText "Beende alle Netzwerkverbindungen...."
sleep 0.2

startFireWall  


#---------------------------------#
# BACKUP CURRENT DESKTOP CONFIG   #
#---------------------------------#
qdbus $progress Set "" value 2
qdbus $progress setLabelText "Sichere entsperrte Desktop Konfiguration.... "
sleep 0.2

backupCurrentConfig

#---------------------------------#
# LOAD EXAM CONFIG                #
#---------------------------------#
qdbus $progress Set "" value 3
qdbus $progress setLabelText "Lade Exam Desktop...."
sleep 0.2

loadExamConfig


#---------------------------------#
# MOUNT SHARE                     #
#---------------------------------#
qdbus $progress Set "" value 4
qdbus $progress setLabelText "Mounte Austauschpartition in das Verzeichnis SHARE...."
sleep 0.2

mountShare

    
    
#---------------------------------#
# CREATE EXAM LOCK FILE           #
#---------------------------------#
qdbus $progress Set "" value 5
qdbus $progress setLabelText "Erstelle Sperrdatei mit Uhrzeit...."
sleep 0.2

createLockFile
    
    
    
#---------------------------------#
# COPY AUTOSTART SCRIPTS          #
#---------------------------------#
qdbus $progress Set "" value 6
qdbus $progress setLabelText "Starte automatische Screenshots...."
sleep 0.2

runAutostartScripts


#--------------------------------------------------------#
# BLOCK ADDITIONAL FEATURES (menuedit, usbmount, etc.)   #
#--------------------------------------------------------#
qdbus $progress Set "" value 7
qdbus $progress setLabelText "Sperre Systemdateien...."
   
blockAdditionalFeatures

   
#---------------------------------#
# FINISH - RESTART DESKTOP        #
#---------------------------------#
qdbus $progress Set "" value 8
qdbus $progress setLabelText "Prüfungsumgebung eingerichtet...  
Starte Desktop neu!"

playSound
#qdbus $progress close
restartDesktop
    
