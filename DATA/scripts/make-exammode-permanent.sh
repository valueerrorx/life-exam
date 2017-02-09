 #!/bin/bash
# last updated: 06.02.2017
# loads exam desktop configuration an makes all settings permanent

# CLIENT FILE #

# dont forget the trailing slash - otherwise shell will think its a file

USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"


IPSFILE="${HOME}.life/EXAM/EXAMCONFIG/EXAM-A-IPS.DB"
CONFIGDIR="${HOME}.life/EXAM/EXAMCONFIG/"
BACKUPDIR="${HOME}.life/unlockedbackup/" #absolute path in order to be accessible from all script locations
LOCKDOWNDIR="${HOME}.life/EXAM/EXAMCONFIG/lockdown/"
EXAMLOCKFILE="${HOME}.life/EXAM/exam.lock"
ABGABE="${HOME}ABGABE/"
SCRIPTDIR="${HOME}.life/EXAM/scripts/"

#--------------------------------#
# Check if root and running exam #
#--------------------------------#
if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox 'You need root privileges - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    exit 1
fi
if [ -f "/etc/kde5rc" ];then
    kdialog  --msgbox 'Desktop is locked - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    exit 1
fi
if [ -f "$EXAMLOCKFILE" ];then
    kdialog  --msgbox 'Already running exam - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
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





kdialog  --caption "LIFE" --title "LIFE" --yesno "Wollen sie diesen USB Stick dauerhaft in den Prüfungsmodus versetzen?

Der fertige USB Stick nutzt die Konfigurationen des Programmes 'Exam Teacher'.
Sie bekommen die Möglichkeit ein Root Passwort festzulegen.
Den USB Stick können sie danach mit Hilfe des LIFE Programmes
'USB Stick Kopie' (Datenpartition übertragen) vervielfältigen!";

if [ ! "$?" = 0 ]; then
    exit  0
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
date > $EXAMLOCKFILE




#---------------------------------#
# BACKUP CURRENT DESKTOP CONFIG   #
#---------------------------------#
qdbus $progress Set "" value 2
qdbus $progress setLabelText "Sichere entsperrte Desktop Konfiguration.... "
sleep 0.5
# we could backup everything from .config .local .kde but i think this is enough
cp -a ${HOME}.config/plasmarc ${BACKUPDIR}
cp -a ${HOME}.config/plasmashellrc ${BACKUPDIR}
cp -a ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc ${BACKUPDIR}
cp -a ${HOME}.kde/share/config/kdeglobals ${BACKUPDIR}
cp -a ${HOME}.config/kwinrc ${BACKUPDIR}
cp -a ${HOME}.config/kglobalshortcutsrc ${BACKUPDIR}
cp -a /usr/share/plasma/plasmoids/org.kde.plasma.quicklaunch/contents/ui/IconItem.qml ${BACKUPDIR}
cp -a /usr/share/plasma/plasmoids/org.kde.plasma.quicklaunch/contents/ui/main.qml ${BACKUPDIR}
cp -a ${HOME}.config/Kingsoft/Office.conf ${BACKUPDIR}
cp -a ${HOME}.config/libreoffice/4/user/registrymodifications.xcu ${BACKUPDIR}
cp -a ${HOME}.local/share/user-places.xbel ${BACKUPDIR}



#----------------------------------------------------------------------------------#
# LOAD COMPLETE EXAM CONFIG -  ALSO LOAD SYSTEMLOCKFILES (kde5rc, etc.) #
#----------------------------------------------------------------------------------#
qdbus $progress Set "" value 3
qdbus $progress setLabelText "Sperre Desktop...."
sleep 0.5

sudo cp ${LOCKDOWNDIR}kde5rc-EXAM /etc/kde5rc
# sudo cp ${LOCKDOWNDIR}xorg.conf /etc/X11
sudo cp ${LOCKDOWNDIR}IconItem.qml-EXAM /usr/share/plasma/plasmoids/org.kde.plasma.quicklaunch/contents/ui/IconItem.qml
sudo cp ${LOCKDOWNDIR}main.qml-EXAM /usr/share/plasma/plasmoids/org.kde.plasma.quicklaunch/contents/ui/main.qml
cp -a ${LOCKDOWNDIR}kglobalshortcutsrc-EXAM ${HOME}.config/kglobalshortcutsrc
cp -a ${LOCKDOWNDIR}Office.conf-EXAM ${HOME}.config/Kingsoft/Office.conf
cp -a ${LOCKDOWNDIR}registrymodifications.xcu-EXAM ${HOME}.config/libreoffice/4/user/registrymodifications.xcu
cp -a ${LOCKDOWNDIR}plasma-EXAM    ${HOME}.config/plasma-org.kde.plasma.desktop-appletsrc      #load minimal plasma config with stop exam icon, libreoffice, dolphin, geogebra, kcalc,#load minimal plasma config with stop exam icon, libreoffice, dolphin, geogebra, kcalc,   
cp -a ${LOCKDOWNDIR}user-places.xbel-EXAM ${HOME}.local/share/user-places.xbel
cp -a ${LOCKDOWNDIR}kwinrc-EXAM ${HOME}.config/kwinrc




#---------------------------------#
# MOUNT ABGABE                    #
#---------------------------------#
qdbus $progress Set "" value 4
qdbus $progress setLabelText "Mounte Austauschpartition in das Verzeichnis ABGABE...."
sleep 0.5

mkdir $ABGABE
sudo mount -o umask=002,uid=1000,gid=1000 /dev/disk/by-label/ABGABE $ABGABE


echo "#!/bin/sh -e" > /etc/rc.local
echo "sudo mount -o umask=002,uid=1000,gid=1000 /dev/disk/by-label/ABGABE /home/student/ABGABE" >> /etc/rc.local
       




#---------------------------------#
# INITIALIZE FIREWALL             #
#---------------------------------#
qdbus $progress Set "" value 5
qdbus $progress setLabelText "Beende alle Netzwerkverbindungen...."
sleep 0.5

setIPtables(){
    #allow loopback 
    sudo iptables -I INPUT 1 -i lo -j ACCEPT
    #allow DNS
    sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
    if [ -f $IPSFILE ]; then
        #allow input and output for ALLOWEDIP
        for IP in `cat $IPSFILE`; do
            echo "exception noticed $IP"
            sudo iptables -A INPUT  -p tcp -d $IP -m multiport --dports 80,443 -j ACCEPT
            sudo iptables -A OUTPUT  -p tcp -d $IP -m multiport --dports 80,443 -j ACCEPT
        done
    fi
    #allow ESTABLISHED and RELATED (important for active server communication)
    sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    sudo iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT
    #drop the rest
    sudo iptables -P INPUT DROP
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
stopIPtables
sleep 1
setIPtables


sudo iptables-save > /etc/iptables.conf    # save IPtables rules to conf file
echo "sudo iptables-restore < /etc/iptables.conf"  >> /etc/rc.local
echo "exit 0" >> /etc/rc.local
        
        




#---------------------------------#
# COPY AUTOSTART SCRIPTS          #
#---------------------------------#
qdbus $progress Set "" value 6
qdbus $progress setLabelText "Starte automatische Screenshots...."

cp ${CONFIGDIR}auto-screenshot.sh ${HOME}.config/autostart-scripts


#---------------------------------#
# COPY USB KOPIE LINK             #
#---------------------------------#
sudo cp "${SCRIPTDIR}USB-Kopie.desktop" $ABGABE


#--------------------------------------------------------#
# BLOCK ADDITIONAL FEATURES (menuedit, usbmount, etc.)   #
#--------------------------------------------------------#
qdbus $progress Set "" value 7
qdbus $progress setLabelText "Sperre Systemdateien...."
sleep 0.5

sudo chmod -x /usr/bin/kmenuedit   # leider ist da immernoch ein bug im kiosk system - daher muss das mit diesem workaround geschehen
sudo chmod -x /sbin/iptables   #make it even harder to unlock networking (+x in stopexam !!)
sudo chmod 700 /media/ -R   # this makes it impossible to mount anything in kubuntu /dolphin




# virtuelle terminals abschalten
sudo systemctl stop getty@tty1.service
sudo systemctl stop getty@tty2.service
sudo systemctl stop getty@tty3.service
sudo systemctl stop getty@tty4.service
sudo systemctl stop getty@tty5.service
sudo systemctl stop getty@tty6.service

sudo chmod -x /sbin/agetty  # start (respawning) von virtuellen terminals auf ctrl+alt+F1-6  verbieten
sudo chmod -x /usr/bin/xterm
sudo chmod -x /usr/bin/konsole
 
 
#---------------------------------#
# SET ROOT PASSWORD               #
#---------------------------------#
 
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
fi;
 
 

#---------------------------------#
# FINISH - RESTART KDE            #
#---------------------------------#

qdbus $progress Set "" value 8
qdbus $progress setLabelText "Prüfungsumgebung eingerichtet...  
Starte Desktop neu!"
sleep 4
qdbus $progress close



##  restart desktop !!

# kill running programs to allow new config to load
#pkill -f dolphin
pkill -f google
pkill -f firefox
pkill -f writer
pkill -f kwrite
pkill -f konsole
pkill -f geogebra

sudo -u ${USER} -H kquitapp5 plasmashell &
sleep 2
exec sudo -u ${USER} -H kstart5 plasmashell &
sleep 2
exec sudo -u ${USER} -H kwin --replace &













