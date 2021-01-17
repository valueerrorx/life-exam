#!/bin/bash
# last updated: 26.01.2017
 
 
# SERVER FILE #


#-----------------------------------------------------#
#  Zeige deine IP 
#-----------------------------------------------------#
IP=$(ip route get 1 | awk '{print $(NF-2);exit}')
IFACE=$(iwconfig 2>/dev/null |grep -o "^\w*")   #get wlan device name
IPW=$(ip -4 address show dev ${IFACE} |grep inet | awk '{print $2}'|cut -d '/' -f 1)



if [[( "$IP" = "") && ( "$IPW" = "" ) ]]; then
    kdialog  --msgbox "Es konnte keine aktive Netzwerkverbindung gefunden werden!" --title 'LIFE'  > /dev/null
elif [[( "$IP" != "") && ( "$IPW" = "" ) ]]; then
    kdialog  --msgbox "Deine derzeitige IP Adresse lautet: \n\n$IP\n" --title 'LIFE'  > /dev/null
elif [[( "$IP" = "") && ( "$IPW" != "" ) ]]; then
    kdialog  --msgbox "Deine derzeitige WLAN IP Adresse lautet: \n\n$IPW\n" --title 'LIFE' > /dev/null
else
    kdialog  --msgbox "Deine derzeitige IP Adresse lautet:\n$IP\n\nDeine WLAN IP Adresse lautet: \n\n$IPW\n" --title 'LIFE' > /dev/null
fi
