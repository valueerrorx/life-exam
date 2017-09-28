#!/bin/bash
# last updated: 13.02.2017
# unloads exam desktop
#
# CLIENT FILE - STOP EXAM
#
# dieses Skript erwartet einen Parameter:   <exam>  <config>  
# es wird dadurch unterschieden ob man nur den konfigurations modus oder den exam modus beendet



USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"
EXAMLOCKFILE="${HOME}.life/EXAM/exam.lock"
BACKUPDIR="${HOME}.life/unlockedbackup/" 
LOCKDOWNDIR="${HOME}.life/EXAM/EXAMCONFIG/lockdown/"
SHARE="${HOME}SHARE/"

MODE=$1
if [[ ( $MODE != "config" ) && ( $MODE != "exam" )  ]]
then
    kdialog  --msgbox 'Parameter is missing <config> <exam> ' --title 'Stopping Exam' --caption "Stopping Exam"
    exit 1
fi


#--------------------------------#
# Check if root and running exam #
#--------------------------------#
if ! [ -f "$EXAMLOCKFILE" ];then
    kdialog  --msgbox 'Not running exam - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    sleep 2
    exit 0
fi

if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox 'You need root privileges - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    exit 1
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

if [[ ( $MODE = "config" ) ]]
then 
    kdialog --yesnocancel "Die Anpassung des Prüfungsdesktops wird beendet.                                                \n\nBitte achten Sie darauf, dass ein Link zum Programm 'Stoppe Prüfungsumgebung' am Desktop erreichbar sein muss.\n\nWollen sie die Änderungen speichern?" --title "EXAM" --caption "EXAM";
    answer="$?";
    if [ "$answer" = 0 ]; then
        #------------------------------------------------#
        # SAVE CURRENT EXAM CONFIG FILES TO LOCKDOWNDIR  #
        #------------------------------------------------#
       
       #kde
        cp -a ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc ${LOCKDOWNDIR}plasma-EXAM  
        cp -a ${HOME}.config/kwinrc ${LOCKDOWNDIR}kwinrc-EXAM

        #office
        cp -a ${HOME}.config/Kingsoft/Office.conf ${LOCKDOWNDIR}Office.conf-EXAM   # wps office
        cp -a ${HOME}.config/libreoffice/4/user/registrymodifications.xcu ${LOCKDOWNDIR}registrymodifications.xcu-EXAM   # libre office
        cp -a ${HOME}.config/calligra* ${LOCKDOWNDIR}  # calligra office (best with kde kiosk)


        #filemanager
        cp -a ${HOME}.local/share/user-places.xbel ${LOCKDOWNDIR}user-places.xbel-EXAM
        cp -a ${HOME}.config/dolphinrc ${LOCKDOWNDIR}dolphinrc-EXAM
        cp -a ${HOME}.config/user-dirs.dirs ${LOCKDOWNDIR}       #default directories for documents music etc.
        cp -a ${HOME}.config/mimeapps.list ${LOCKDOWNDIR}mimeapps.list-EXAM
        
        sudo rm "${SHARE}Speichere Prüfungsumgebung.desktop"
    elif [ "$answer" = 1 ]; then
        #------------------------------------------------#
        # CONTINUE WITHOUT SAVING                        #
        #------------------------------------------------#
        sudo rm "${SHARE}Speichere Prüfungsumgebung.desktop"
    else
        exit 1   #cancel
    fi;

fi

if [[ ( $MODE = "exam" ) ]]
then 
    kdialog --warningcontinuecancel "Prüfungsumgebung beenden?\nHaben sie ihre Arbeit im Ordner SHARE gesichert ? " --title "EXAM" --caption "EXAM";
    if [ "$?" = 0 ]; then
        sleep 0
    else
        exit 1   #cancel
    fi;
fi   




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

    cp -a ${BACKUPDIR}plasma-org.kde.plasma.desktop-appletsrc ${HOME}.config/
    cp -a ${BACKUPDIR}kwinrc ${HOME}.config/

    cp -a ${BACKUPDIR}Office.conf ${HOME}.config/Kingsoft/
    cp -a ${BACKUPDIR}registrymodifications.xcu ${HOME}.config/libreoffice/4/user/
    cp -a ${BACKUPDIR}user-places.xbel ${HOME}.local/share/
    cp -a ${BACKUPDIR}dolphinrc ${HOME}.config/
    cp -a ${BACKUPDIR}calligra* ${HOME}.config/
    cp -a ${BACKUPDIR}user-dirs.dirs ${HOME}.config/
    cp -a ${BACKUPDIR}mimeapps.list ${HOME}.config/
    cp -a ${BACKUPDIR}mimeapps.list ${HOME}.local/share/applications/
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
# UMOUNT SHARE                   #
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
    if [[ ( $MODE = "exam" ) ]]
    then 
        sudo chmod 755 /sbin/iptables   # nachdem eh kein terminal erlaubt ist ist es fraglich ob das notwendig ist
        sudo chmod 755 /media/ -R  # allow mounting again
        sudo chmod 755 /sbin/agetty  # start (respawning) von virtuellen terminals auf ctrl+alt+F[1-6]  erlauben
        sudo chmod 755 /usr/bin/xterm 
        sudo chmod 755 /usr/bin/konsole

        sudo rm /etc/kde5rc        #kde plasma KIOSK wieder aufheben
    fi

    
    
    
    
#-------------------------------------------#
# STOP AUTO SCREENSHOTS AND AUTO FIREWALL   #
#-------------------------------------------#
qdbus $progress Set "" value 4
qdbus $progress setLabelText "Stoppe automatische Screenshots...."   
   
    rm  ${HOME}.config/autostart-scripts/auto-screenshot.sh
    sudo killall auto-screenshot.sh && sudo pkill -f auto-screenshot

    # entferne firewall einträge (standalone-exam mode advanced)
    echo "#!/bin/sh -e" > /etc/rc.local
    echo "exit 0" >> /etc/rc.local


    
    

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
qdbus $progress setLabelText "Passwort wird zurückgesetzt...."
    
    if [[ ( $MODE = "exam" ) ]]
    then 
        # falls ein rootpasswort vom lehrer gesetzt wurde (standalone-exam mode advanced)
        sudo sed -i "/student/c\student:U6aMy0wojraho:16233:0:99999:7:::" /etc/shadow
    fi
    
    
    
    
    
    
    
    
    
    
    
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

    # pkill -f dolphin && killall dolphin   #nachdem die testscripte oft aus dolphin gestartet werden wird dieser in der entwicklungsphase noch ausgespart
    pkill -f google && killall google-chrome && killall google-chrome-stable
    pkill -f firefox  && killall firefox
    pkill -f writer && killall writer
    pkill -f konsole && killall konsole
    pkill -f geogebra && killall geogebra

    sudo -u ${USER} -H kquitapp5 plasmashell &
    sleep 2
    exec sudo -u ${USER} -H kstart5 plasmashell &
    sleep 2
    exec sudo -u ${USER} -H kwin --replace &

























