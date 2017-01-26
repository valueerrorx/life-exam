#!/bin/bash
# last updated: 26.01.2017
# prüfungsumgebung beenden normale konfiguration wiederherstellen

# CLIENT FILE #


BACKUPDIR="./FILESCLIENT/EXAMCONFIG/unlockedbackup"
LOCKDOWNDIR="./FILESCLIENT/EXAMCONFIG/lockdown"



if [ "$(id -u)" != "0" ]; then
    kdialog  --msgbox 'You need root privileges - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    exit 1
fi
if ! [ -f "exam" ];then
    kdialog  --msgbox 'Not running exam - Stopping program' --title 'Starting Exam' --caption "Starting Exam"
    sleep 2
    exit 0
fi







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






kdialog --warningcontinuecancel "Prüfungsumgebung beenden?\nHaben sie ihre Arbeit im Ordner ABGABE gesichert ? " --title "EXAM" --caption "EXAM";
if [ "$?" = 0 ]; then
    sleep 0
else
    exit 1 
fi;
    
## start progress with a lot of spaces (defines the width of the window - using geometry will move the window out of the center)
progress=$(kdialog --progressbar "Beende Prüfungsumgebung                                                               ");
qdbus $progress Set "" maximum 6
sleep 0.5


    #---------------------------------#
    # RESTORE PREVIOUS DESKTOP CONFIG #
    #---------------------------------#
    qdbus $progress Set "" value 1
    qdbus $progress setLabelText "Stelle entsperrte Desktop Konfiguration wieder her.... "
    sleep 0.5

    cp -a ${BACKUPDIR}/plasmarc /home/student/.config/
    cp -a ${BACKUPDIR}/plasmashellrc /home/student/.config/ 
    cp -a ${BACKUPDIR}/plasma-org.kde.plasma.desktop-appletsrc /home/student/.config/
    cp -a ${BACKUPDIR}/kdeglobals /home/student/.kde/share/config/
    cp -a ${BACKUPDIR}/kwinrc /home/student/.config/
    cp -a ${BACKUPDIR}/kglobalshortcutsrc /home/student/.config/
    sudo cp -a ${BACKUPDIR}/IconItem.qml /usr/share/plasma/plasmoids/org.kde.plasma.quicklaunch/contents/ui/
    sudo cp -a ${BACKUPDIR}/main.qml /usr/share/plasma/plasmoids/org.kde.plasma.quicklaunch/contents/ui/
    cp -a ${BACKUPDIR}/Office.conf /home/student/.config/Kingsoft/
    cp -a ${BACKUPDIR}/registrymodifications.xcu /home/student/.config/libreoffice/4/user/
    cp -a ${BACKUPDIR}/user-places.xbel /home/student/.local/share/
    
    # sichere exam start und end infos
    date >> exam
    sudo cp exam /home/student/ABGABE/
    sleep 0.5
    
    #---------------------------------#
    # UMOUNT ABGABE                   #
    #---------------------------------#
    qdbus $progress Set "" value 2
    qdbus $progress setLabelText "Verzeichnis ABGABE wird freigegeben...."
    sleep 0.5
    sudo umount -l /home/student/ABGABE
    
    
    
    #---------------------------------#
    # UNLOCK SYSTEM FILES             #
    #---------------------------------#
    qdbus $progress Set "" value 3
    qdbus $progress setLabelText "Systemdateien werden entsperrt...."
    sleep 0.5
    sudo chmod +x /usr/bin/kmenuedit
    sudo chmod 755 /media/ -R  # allow mounting again
    sudo chmod +x /sbin/iptables   # nachdem eh kein terminal erlaubt ist ist es fraglich ob das notwendig ist
    sudo rm /etc/kde5rc
    sudo rm /etc/X11/xorg.conf
    sudo rm exam   #remove this file otherwise LIFE will think exam is still running
    
    
    
    #---------------------------------#
    # STOP AUTO SCREENSHOTS           #
    #---------------------------------#
    qdbus $progress Set "" value 4
    qdbus $progress setLabelText "Stoppe automatische Screenshots...."   
    rm  /home/student/.config/autostart-scripts/auto-screenshot.sh
    sudo killall auto-screenshot.sh
    rmdir /home/student/ABGABE
    
    
    #---------------------------------#
    # STOP FIREWALL                   #
    #---------------------------------#
    qdbus $progress Set "" value 5
    qdbus $progress setLabelText "Aktiviere Netzwerkverbindungen...."
    sleep 0.5
    stopIPtables

    
    #play sound
    amixer -D pulse sset Master 90% > /dev/null 2>&1
    pactl set-sink-volume 0 90%
    # paplay /usr/share/sounds/KDE-Sys-Question.ogg
    paplay /usr/share/sounds/KDE-Sys-App-Error-Serious-Very.ogg

    qdbus $progress Set "" value 6
    qdbus $progress setLabelText "Prüfungsumgebung angehalten...  
Starte Desktop neu!"
    sleep 4
    qdbus $progress close

    sudo killall Xorg
    































