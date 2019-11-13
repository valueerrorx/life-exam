#!/bin/bash
# last updated: 16.11.2018
# unloads exam desktop
#
# CLIENT FILE - STOP EXAM



USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"
EXAMLOCKFILE="${HOME}.life/EXAM/exam.lock"
BACKUPDIR="${HOME}.life/unlockedbackup/" 
LOCKDOWNDIR="${HOME}.life/EXAM/EXAMCONFIG/lockdown/"
SHARE="${HOME}SHARE/"


DELSHARE=$1


#--------------------------------#
# Check if root and running exam #
#--------------------------------#
if ! [ -f "$EXAMLOCKFILE" ];then
    kdialog  --msgbox 'Not running exam - Stopping program' --title 'Starting Exam'
    sleep 2
    exit 0
fi

if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox 'You need root privileges - Stopping program' --title 'Starting Exam'
    exit 0
fi




# this function removes the firewall #
stopIPtables(){
    sudo iptables -P INPUT ACCEPT
    sudo iptables -P FORWARD ACCEPT
    sudo iptables -P OUTPUT ACCEPT
    sudo iptables -F
    sudo iptables -X
    sudo iptables -t nat -F
    sudo iptables -t nat -X
    sudo iptables -t mangle -F
    sudo iptables -t mangle -X
    sudo iptables -t raw -F 
    sudo iptables -t raw -X
}






#--------------------------------#
# ASK FOR CONFIRMATION           #
#--------------------------------#


    kdialog --warningcontinuecancel "Prüfungsumgebung beenden?\nHaben sie ihre Arbeit im Ordner SHARE gesichert ? " --title "EXAM";
    if [ "$?" = 0 ]; then
        sleep 0
    else
        exit 1   #cancel
    fi;
  




#---------------------------------#
# OPEN PROGRESSBAR DIALOG         #
#---------------------------------#
## start progress with a lot of spaces (defines the width of the window - using geometry will move the window out of the center)
progress=$(kdialog --progressbar "Beende Prüfungsumgebung                                                               ");
qdbus $progress Set "" maximum 7
sleep 0.5






#---------------------------------#
# RESTORE PREVIOUS DESKTOP CONFIG #
#---------------------------------#
qdbus $progress Set "" value 1
qdbus $progress setLabelText "Stelle entsperrte Desktop Konfiguration wieder her.... "
sleep 0.5

    sudo rm /etc/kde5rc        #kde plasma KIOSK wieder aufheben

    cp -a ${BACKUPDIR}plasma-org.kde.plasma.desktop-appletsrc ${HOME}.config/
    cp -a ${BACKUPDIR}kwinrc ${HOME}.config/

    #cp -a ${BACKUPDIR}Office.conf ${HOME}.config/Kingsoft/
    cp -a ${BACKUPDIR}registrymodifications.xcu ${HOME}.config/libreoffice/4/user/
    cp -a ${BACKUPDIR}user-places.xbel ${HOME}.local/share/
    cp -a ${BACKUPDIR}dolphinrc ${HOME}.config/
    cp -a ${BACKUPDIR}calligra* ${HOME}.config/
    cp -a ${BACKUPDIR}user-dirs.dirs ${HOME}.config/
    cp -a ${BACKUPDIR}mimeapps.list ${HOME}.config/
    cp -a ${BACKUPDIR}mimeapps.list ${HOME}.local/share/applications/
    cp -a ${BACKUPDIR}Preferences ${HOME}.config/google-chrome/Default/Preferences
    
    sudo cp -a ${BACKUPDIR}mimeapps.list /usr/share/applications/mimeapps.list

    qdbus org.kde.kglobalaccel /kglobalaccel blockGlobalShortcuts false   #UN-block all global short cuts ( like alt+space for krunner)



#---------------------------------#
# REMOVE EXAM LOCKFILE            #
#---------------------------------#
    # sichere exam start und end infos
    date >> $EXAMLOCKFILE
    sudo cp $EXAMLOCKFILE $SHARE
    sudo rm $EXAMLOCKFILE
    sleep 0.5


  
  
#---------------------------------#
# CLEAN  SHARE                    #   
#---------------------------------#

if [[ ( $DELSHARE = "2" ) ]]     #checkbox sends 0 for unchecked and 2 for checked
then
    sudo rm -rf ${SHARE}*
    sudo rm -rf ${SHARE}.* 
fi 
    


#---------------------------------#
# UMOUNT SHARE                    #    SHARE is now permanently mounted on life sticks
#---------------------------------#
qdbus $progress Set "" value 2
#qdbus $progress setLabelText "Verzeichnis SHARE wird freigegeben...."
sleep 0.5
   # sudo umount -l $SHARE


    
    
    
    

#---------------------------------#
# UNLOCK SYSTEM FILES             #
#---------------------------------#
qdbus $progress Set "" value 3
qdbus $progress setLabelText "Systemdateien werden entsperrt...."
sleep 0.5

#         sudo chmod 755 /sbin/iptables   # nachdem eh kein terminal erlaubt ist ist es fraglich ob das notwendig ist
        sudo chmod 755 /sbin/agetty  # start (respawning) von virtuellen terminals auf ctrl+alt+F[1-6]  erlauben
        sudo chmod 755 /usr/bin/xterm 
        sudo chmod 755 /usr/bin/konsole
      
       
        sudo umount /media/*
        sudo umount /media/student/*
        sudo umount -l /media/*
        sudo umount -l /media/student/*
        sleep 1
        
        
        MOUNTED=$(df -h |grep media |wc -l)
        if [[( $MOUNTED = "1" )]]
        then
            sleep 0 #do nothing - don't mess up rights of mounted partition there
        else
            # allow mounting again 
            sudo chmod 755 /media/ -R  
        fi

        
        
     
       
    
    
    
    
#-------------------------------------------#
# STOP AUTO SCREENSHOTS AND AUTO FIREWALL   #
#-------------------------------------------#
qdbus $progress Set "" value 4
qdbus $progress setLabelText "Stoppe automatische Screenshots...."   
   
    rm  ${HOME}.config/autostart-scripts/auto-screenshot.sh
    sudo killall auto-screenshot.sh && sudo pkill -f auto-screenshot

    # entferne firewall einträge (standalone-exam mode advanced)
    #echo "#!/bin/sh -e" > /etc/rc.local
    #echo "exit 0" >> /etc/rc.local


    
    

#---------------------------------#
# STOP FIREWALL                   #
#---------------------------------#
qdbus $progress Set "" value 5
qdbus $progress setLabelText "Aktiviere Netzwerkverbindungen...."
sleep 0.5

    stopIPtables

    
    
    
    
    

#---------------------------------#
# REMOVE ROOT PASSWORD            #
#---------------------------------#
qdbus $progress Set "" value 6
#qdbus $progress setLabelText "Passwort wird zurückgesetzt...."
    

        # falls ein rootpasswort vom lehrer gesetzt wurde (standalone-exam mode advanced)
        #sudo sed -i "/student/c\student:U6aMy0wojraho:16233:0:99999:7:::" /etc/shadow

    
    
    
    
    
    
    
    
    
    
    
#----------------------------------------------#
# FINISH - RESTART AND LOAD DEFAULT DESKTOP    #
#----------------------------------------------#
qdbus $progress Set "" value 7
qdbus $progress setLabelText "Prüfungsumgebung angehalten...  
Starte Desktop neu!"
sleep 4
qdbus $progress close

    amixer -D pulse sset Master 90% > /dev/null 2>&1
    pactl set-sink-volume 0 90%
    paplay /usr/share/sounds/KDE-Sys-App-Error-Serious-Very.ogg

    
    pkill -f Xorg
    
#     # pkill -f dolphin && killall dolphin   #nachdem die testscripte oft aus dolphin gestartet werden wird dieser in der entwicklungsphase noch ausgespart
#     pkill -f google && killall google-chrome && killall google-chrome-stable
#     pkill -f firefox  && killall firefox
#     pkill -f writer && killall writer
#     pkill -f konsole && killall konsole
#     pkill -f geogebra && killall geogebra
# 
#     kquitapp5 plasmashell &
#     sleep 2
#     kstart5 plasmashell &
#     sleep 2
#     kwin --replace &

























