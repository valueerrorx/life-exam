#!/bin/bash
# last updated: 13.02.2017
# loads exam desktop configuration
#
# CLIENT FILE - START EXAM
#
# dieses Skript erwartet einen Parameter:   <exam>  <config>  <permanent>
# es wird dadurch unterschieden ob man den konfigurations modus oder den exam modus (oder permanent) startet




# dont forget the trailing slash - otherwise shell will think its a file
USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"
IPSFILE="${HOME}.life/EXAM/EXAMCONFIG/EXAM-A-IPS.DB"
CONFIGDIR="${HOME}.life/EXAM/EXAMCONFIG/"
BACKUPDIR="${HOME}.life/unlockedbackup/" #absolute path in order to be accessible from all script locations
LOCKDOWNDIR="${HOME}.life/EXAM/EXAMCONFIG/lockdown/"
EXAMLOCKFILE="${HOME}.life/EXAM/exam.lock"
SHARE="${HOME}SHARE/"
SCRIPTDIR="${HOME}.life/EXAM/scripts/"

MODE=$1
SUBJECT=$2




if [[ ( $MODE != "config" ) && ( $MODE != "exam" )  && ( $MODE != "permanent" )   ]]
then
    kdialog  --msgbox 'Parameter is missing <config> <exam> <permanent>' --title 'Starting Exam' --caption "Starting Exam"
    exit 1
fi

if [[ ( $MODE = "config" ) ]]
then
    if [[ ( $SUBJECT = "math" ) ]]
    then
        DESKTOPNAME="Mathematik"
    else
        DESKTOPNAME="Sprachen/Deutsch"
    fi
    kdialog  --yesno "Wollen sie den Exam Desktop für $DESKTOPNAME manuell anpassen?" --title 'Starting Exam' --caption "Starting Exam"
    if [ "$?" = 0 ]; then
        sleep 0
    else
        exit 1
    fi
fi



#--------------------------------#
# Check if root and running exam #
#--------------------------------#
if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox 'You need root privileges - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    exit 1
fi
if [ -f "$EXAMLOCKFILE" ];then
    kdialog  --yesno "Already running exam! \nDo you want to reload the Exam-Desktop?"  --title 'Starting Exam' --caption "Starting Exam"
    # this way we could restart the desktop in exam mode just in case plasma or kwin did not start properly
    if [ ! "$?" = 0 ]; then
        exit  0   #cancel
    else
    sudo -u ${USER} -H kquitapp5 plasmashell & sleep 2
    exec sudo -u ${USER} -H kstart5 plasmashell &
    exec sudo -u ${USER} -H kwin --replace &
    exit 0
    fi

fi
if [ -f "/etc/kde5rc" ];then
    kdialog  --msgbox 'Desktop is already locked - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    exit 1
fi
if [ ! -d "$BACKUPDIR" ];then
    mkdir -p $BACKUPDIR
fi



#---------------------------------------------------#
# Check for PERMANENT MODE and ask for confirmation #
#---------------------------------------------------#

if [[ ( $MODE = "permanent" ) ]]
then 
    kdialog  --caption "LIFE" --title "LIFE" --yesno "Wollen sie diesen USB Stick dauerhaft in den Prüfungsmodus versetzen?

    Der fertige USB Stick nutzt die Konfigurationen des Programmes 'Exam Teacher'.
    Sie bekommen die Möglichkeit ein Root Passwort festzulegen.
    Den USB Stick können sie danach mit Hilfe des LIFE Programmes
    'USB Stick Kopie' (Datenpartition übertragen) vervielfältigen!";

    if [ ! "$?" = 0 ]; then
        exit  0   #cancel
    fi
fi














#---------------------------------#
# OPEN PROGRESSBAR DIALOG         #
#---------------------------------#
## start progress with a lot of spaces (defines the width of the window - using geometry will move the window out of the center)
progress=$(kdialog --progressbar "Starte Prüfungsumgebung                                                               "); > /dev/null
qdbus $progress Set "" maximum 8
sleep 0.5
#---------------------------------#
# CREATE EXAM LOCK FILE           #
#---------------------------------#
qdbus $progress Set "" value 1
qdbus $progress setLabelText "Erstelle Sperrdatei mit Uhrzeit...."
sleep 0.5

    touch $EXAMLOCKFILE
    echo $SUBJECT > $EXAMLOCKFILE   # write subject into lockfile in order to read from it when the exam desktop should be stored
    sudo chown ${USER}:${USER} $EXAMLOCKFILE      # twistd runs as root - fix permissions










#---------------------------------#
# BACKUP CURRENT DESKTOP CONFIG   #
#---------------------------------#
qdbus $progress Set "" value 2
qdbus $progress setLabelText "Sichere entsperrte Desktop Konfiguration.... "
sleep 0.5
    #kde
    cp -a ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc ${BACKUPDIR}   #main desktop applets config file
    cp -a ${HOME}.config/kwinrc ${BACKUPDIR}        # windowmanager configuration
    cp -a ${HOME}.config/kglobalshortcutsrc ${BACKUPDIR}   # keyboardshortcuts
    
    #office
    cp -a ${HOME}.config/libreoffice/4/user/registrymodifications.xcu ${BACKUPDIR}
    cp -a ${HOME}.config/calligra* ${BACKUPDIR}
    
    #filemanagment
    cp -a ${HOME}.local/share/user-places.xbel ${BACKUPDIR}   # dolphin / filepicker places panel config
    cp -a ${HOME}.config/dolphinrc ${BACKUPDIR}    
    cp -a ${HOME}.config/user-dirs.dirs ${BACKUPDIR}  #default directories for documents music etc.
    cp -a ${HOME}.config/mimeapps.list ${BACKUPDIR}
    
    sudo chown -R ${USER}:${USER} ${BACKUPDIR}  # twistd runs as root - fix ownership




    
    




#-----------------------------------------------#
#           LOAD EXAM CONFIG                    #
#-----------------------------------------------#
qdbus $progress Set "" value 3
qdbus $progress setLabelText "Lade Exam Desktop...."
sleep 0.5
    if [[ ( $SUBJECT = "math" ) ]]
    then
        cp -a ${LOCKDOWNDIR}plasma-EXAM-M    ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc      #load minimal plasma config for exam Mathematik
    else
        cp -a ${LOCKDOWNDIR}plasma-EXAM-L    ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc      #load minimal plasma config for exam Deutsch/Sprachen
    fi



    cp -a ${LOCKDOWNDIR}kwinrc-EXAM ${HOME}.config/kwinrc  #special windowmanager settings

    cp -a ${LOCKDOWNDIR}registrymodifications.xcu-EXAM ${HOME}.config/libreoffice/4/user/registrymodifications.xcu
    cp -a ${LOCKDOWNDIR}user-places.xbel-EXAM ${HOME}.local/share/user-places.xbel
    cp -a ${LOCKDOWNDIR}dolphinrc-EXAM ${HOME}.config/dolphinrc
    cp -a ${LOCKDOWNDIR}calligra* ${HOME}.config/
    cp -a ${LOCKDOWNDIR}user-dirs.dirs ${HOME}.config/
    cp -a ${LOCKDOWNDIR}mimeapps.list-EXAM ${HOME}.config/mimeapps.list
    cp -a ${LOCKDOWNDIR}mimeapps.list-EXAM ${HOME}.local/share/applications/mimeapps.list
    sudo cp -a ${LOCKDOWNDIR}mimeapps.list-EXAM /usr/share/applications/mimeapps.list

if [[ ( $MODE = "exam" ) || ( $MODE = "permanent" ) ]]    # LOCK DOWN
then    
    sudo cp ${LOCKDOWNDIR}kde5rc-EXAM /etc/kde5rc   #this is responsible for the KIOSK settings (main lock file)
    sudo chmod 644 /etc/kde5rc     #this is necessary if the script is run form twistd plugin as root
    sudo chown -R ${USER}:${USER} ${HOME}.config/     # twistd runs as root - fix ownership
    sudo chown -R ${USER}:${USER} ${HOME}.local/
fi





    
    
    


#---------------------------------#
# MOUNT SHARE                    #
#---------------------------------#
qdbus $progress Set "" value 4
qdbus $progress setLabelText "Mounte Austauschpartition in das Verzeichnis SHARE...."
sleep 0.5

    mkdir $SHARE > /dev/null 2>&1
    sudo chown -R ${USER}:${USER} $SHARE   # twistd runs as root - fix permissions
    sudo mount -o umask=002,uid=1000,gid=1000 /dev/disk/by-label/SHARE $SHARE
    sudo touch $SHARE   # update timestamp on live usb devices

    if [[  ( $MODE = "permanent" ) ]]
    then 
        echo "#!/bin/sh -e" > /etc/rc.local
        echo "sudo mount -o umask=002,uid=1000,gid=1000 /dev/disk/by-label/SHARE /home/student/SHARE" >> /etc/rc.local
        sudo cp "${SCRIPTDIR}USB-Kopie.desktop" $SHARE
    fi
    
    if [[ ( $MODE = "config" ) ]]
    then
        sudo cp "${SCRIPTDIR}Speichere Prüfungsumgebung.desktop" $SHARE  # erstelle link um config zu speichern
       
    fi




    
    
    

#---------------------------------#
# INITIALIZE FIREWALL             #
#---------------------------------#
qdbus $progress Set "" value 5
qdbus $progress setLabelText "Beende alle Netzwerkverbindungen...."
sleep 0.5

    setIPtables(){
        sudo iptables -I INPUT 1 -i lo -j ACCEPT        #allow loopback 
        sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT     #allow DNS

        if [ -f $IPSFILE ]; then
            for IP in `cat $IPSFILE`; do        #allow input and output for ALLOWEDIP
                echo "exception noticed $IP"
                IPPORTARRAY=(${IP//:/ })
                # destination - destinationports
                sudo iptables -A INPUT  -p tcp -d ${IPPORTARRAY[0]} -m multiport --dports ${IPPORTARRAY[1]},5000 -j ACCEPT
                sudo iptables -A OUTPUT  -p tcp -d ${IPPORTARRAY[0]} -m multiport --dports ${IPPORTARRAY[1]},5000 -j ACCEPT

                # source - destinationports
                sudo iptables -A INPUT  -p tcp -s ${IPPORTARRAY[0]} -m multiport --dports ${IPPORTARRAY[1]},5000 -j ACCEPT
                sudo iptables -A OUTPUT  -p tcp -s ${IPPORTARRAY[0]} -m multiport --dports ${IPPORTARRAY[1]},5000 -j ACCEPT

                # destination - sourceports
                sudo iptables -A INPUT  -p tcp -d ${IPPORTARRAY[0]} -m multiport --sports ${IPPORTARRAY[1]},5000 -j ACCEPT
                sudo iptables -A OUTPUT  -p tcp -d ${IPPORTARRAY[0]} -m multiport --sports ${IPPORTARRAY[1]},5000 -j ACCEPT

                # source - sourceports
                sudo iptables -A INPUT  -p tcp -s ${IPPORTARRAY[0]} -m multiport --sports ${IPPORTARRAY[1]},5000 -j ACCEPT
                sudo iptables -A OUTPUT  -p tcp -s ${IPPORTARRAY[0]} -m multiport --sports ${IPPORTARRAY[1]},5000 -j ACCEPT

            done
        fi
        sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT         #allow ESTABLISHED and RELATED (important for active server communication)
        sudo iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT
        #sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT  # castrated VPS 

        #needed for multicast (twisted)  Multicast Address for Address Allocation for Private Internets
        sudo iptables -A INPUT -p udp -d 228.0.0.5/4 --dport 8005 -j ACCEPT
        sudo iptables -A OUTPUT -p udp -d 228.0.0.5/4 --dport 8005 -j ACCEPT

        sleep 1

        sudo iptables -P INPUT DROP          #drop the rest
        sudo iptables -P OUTPUT DROP
    }
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
    
    if [[ ( $MODE = "exam" ) || ( $MODE = "permanent" ) ]]
    then  
        stopIPtables
        sleep 2
        setIPtables

    fi
    if [[  ( $MODE = "permanent" ) ]]
    then 
        sudo iptables-save > /etc/iptables.conf    # save IPtables rules to conf file
        echo "sudo iptables-restore < /etc/iptables.conf"  >> /etc/rc.local
        echo "exit 0" >> /etc/rc.local
    fi

    
    
    
    
    
    
    
    
    
#---------------------------------#
# COPY AUTOSTART SCRIPTS          #
#---------------------------------#
#FIXME anstelle automatischer screenshots wäre es besser bei jeder "abgabe" diese auch lokal zu archivieren

qdbus $progress Set "" value 6
qdbus $progress setLabelText "Starte automatische Screenshots...."

    if [[ ( $MODE = "exam" ) || ( $MODE = "permanent" ) ]]
    then 
        cp ${CONFIGDIR}auto-screenshot.sh ${HOME}.config/autostart-scripts
        sudo chown -R ${USER}:${USER} ${HOME}.config/autostart-scripts  # twistd runs as root - fix permissions
        sudo chmod -R 755 ${HOME}.config/autostart-scripts
        nohup sudo -u ${USER} -H ${HOME}.config/autostart-scripts/auto-screenshot.sh  >/dev/null 2>&1 &
    fi










#--------------------------------------------------------#
# BLOCK ADDITIONAL FEATURES (menuedit, usbmount, etc.)   #
#--------------------------------------------------------#
qdbus $progress Set "" value 7
qdbus $progress setLabelText "Sperre Systemdateien...."
sleep 0.5

    if [[ ( $MODE = "exam" ) || ( $MODE = "permanent" ) ]]
    then 
        sudo chmod 644 /sbin/iptables   #make it even harder to unlock networking (+x in stopexam !!)
        
        #make sure nothing is mounted in /media  !! IMPORTANT !! otherwise this will mess up the user rights on mounted partitions
        
        sudo umount /media/*
        sudo umount /media/student/*
        sudo umount -l /media/*
        sudo umount -l /media/student/*
        
        sudo chmod 600 /media/ -R   # this makes it impossible to mount anything in kubuntu /dolphin   !!! could be fatal if something is mounted there already  for examle "casper-rw" (this would immediately kill the flashdrive)
       
        sudo chmod 644 /sbin/agetty  # start (respawning) von virtuellen terminals auf ctrl+alt+F[1-6]  verbieten
        sudo chmod 644 /usr/bin/xterm
        sudo chmod 644 /usr/bin/konsole

        sudo systemctl stop getty@tty1.service      # laufende virtuelle terminals abschalten
        sudo systemctl stop getty@tty2.service
        sudo systemctl stop getty@tty3.service
        sudo systemctl stop getty@tty4.service
        sudo systemctl stop getty@tty5.service
        sudo systemctl stop getty@tty6.service
    fi

 
   
   
   
   
   
   
   
  
if [[  ( $MODE = "permanent" ) ]]
then
    #----------------------------------------------------#
    # SET ROOT PASSWORD   (Permanent Exam Mode only      #
    #----------------------------------------------------#
    
    PW="empty"
    getROOT(){
        PASSWD1=$(kdialog  --caption "LIFE" --title "LIFE" --inputbox "Geben sie bitte das gwünschte ROOT Passwort an!");
        if [ "$?" = 0 ]; then
            PASSWD2=$(kdialog  --caption "LIFE" --title "LIFE" --inputbox 'Geben sie bitte das gewünschte ROOT Passwort ein zweites mal an!');
            if [ "$?" = 0 ]; then
            
                if [ "$PASSWD2" = "$PASSWD1"  ]; then
                    sudo -u ${USER} kdialog  --caption "LIFE" --title "LIFE" --passivepopup "Passwort OK!" 3
                    PW=$PASSWD1
                else
                    kdialog  --caption "LIFE" --title "LIFE" --error "Die Passwörter sind nicht ident!"
                    getROOT 
                fi
            else
                kdialog  --caption "LIFE" --title "LIFE" --error "Kein Root Password gesetzt!"
                sleep 0
            fi
        else
            kdialog  --caption "LIFE" --title "LIFE" --error "Kein Root Password gesetzt!"
            sleep 0
        fi
    }
    getROOT
    
    if [ "$PW" != "empty" ]; then
        #setze root passwort
        echo "setze root passwort"
        echo -e "$PW\n$PW"|sudo passwd student
    fi
fi  
   
   
   
   
   
   
   
   
   
#---------------------------------#
# FINISH - RESTART DESKTOP        #
#---------------------------------#
qdbus $progress Set "" value 8
qdbus $progress setLabelText "Prüfungsumgebung eingerichtet...  
Starte Desktop neu!"
sleep 4
qdbus $progress close

    amixer -D pulse sset Master 90% > /dev/null 2>&1
    pactl set-sink-volume 0 90%
    paplay /usr/share/sounds/KDE-Sys-Question.ogg

    #FIXME man könnte auch einfach ksmserver neustarten bzw. Xorg - dann würde kein programm überdauern (derzeit aber unpraktisch und etwas brachial)

    # pkill -f dolphin && killall dolphin   #nachdem die testscripte oft aus dolphin gestartet werden wird dieser in der entwicklungsphase noch ausgespart
    pkill -f google && killall google-chrome && killall google-chrome-stable
    pkill -f firefox  && killall firefox
    pkill -f writer && killall writer
    pkill -f konsole && killall konsole
    pkill -f geogebra && killall geogebra
    pkill -f kate && killall kate

    sudo -u ${USER} -H kquitapp5 plasmashell &
    sleep 2
    exec sudo -u ${USER} -H kstart5 plasmashell &
    sleep 2
    exec sudo -u ${USER} -H kwin --replace &
    sleep 4
    exec sudo -u ${USER} -H qdbus org.kde.kglobalaccel /kglobalaccel blockGlobalShortcuts true   #block all global short cuts ( like alt+space for krunner)
    
















