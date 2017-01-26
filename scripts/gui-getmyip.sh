#!/bin/bash
# last updated: 26.01.2017
 
 
# SERVER FILE #



IP=$(ip route get 1 | awk '{print $NF;exit}')



IFACE=$(iwconfig 2>/dev/null |grep -o "^\w*")   #get wlan device name
IPW=$(ip -4 address show dev ${IFACE} |grep inet | awk '{print $2}'|cut -d '/' -f 1)


if [ "$IP" = "" ]; then
    kdialog  --msgbox "Deine derzeitige IP Adresse lautet:\n\n$IP" --title 'LIFE' --caption "LIFE" > /dev/null
else
    kdialog  --msgbox "Deine derzeitige IP Adresse lautet:\n$IP\n\nDeine WLAN IP Adresse lautet: \n$IPW  " --title 'LIFE' --caption "LIFE" > /dev/null
fi
