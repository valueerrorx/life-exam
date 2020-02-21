#!/bin/bash
# last updated: 26.01.2017

# SERVER FILE #



USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"

IPSFILE="${HOME}.life/EXAM/EXAMCONFIG/EXAM-A-IPS.DB"

# cat $IPSFILE
# 10.0.0.1, 80
# 10.2.2.22, 443
# IPPORTARRAY = [ [10.0.01] , [80] ]



setIPtables(){
        sudo iptables -I INPUT 1 -i lo -j ACCEPT        #allow loopback
        sudo iptables -A INPUT -i lo -j ACCEPT 
        sudo iptables -A OUTPUT -o lo -j ACCEPT
        
        sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT     #allow DNS
        sudo iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT     #allow DNS
        sudo iptables -A OUTPUT -p udp --dport 137 -j ACCEPT     #allow WINS
        
        #allow IPP,TPS,PCL,snmp,mDNS for network printing
        sudo iptables -A INPUT -p tcp -m multiport --dports 631,515,9100,9101,9102,161,139,5353  -j ACCEPT  
        sudo iptables -A OUTPUT -p tcp -m multiport --dports 631,515,9100,9101,9102,161,139,5353 -j ACCEPT 
        sudo iptables -A INPUT -p tcp -m multiport --sports 631,515,9100,9101,9102,161,139,5353 -j ACCEPT  
        sudo iptables -A OUTPUT -p tcp -m multiport --sports 631,515,9100,9101,9102,161,139,5353 -j ACCEPT 
        
        sudo iptables -A INPUT -p udp -m multiport --dports 631,515,9100,9101,9102,161,139,5353  -j ACCEPT
        sudo iptables -A OUTPUT -p udp -m multiport --dports 631,515,9100,9101,9102,161,139,5353 -j ACCEPT 
        sudo iptables -A INPUT -p udp -m multiport --sports 631,515,9100,9101,9102,161,139,5353 -j ACCEPT  
        sudo iptables -A OUTPUT -p udp -m multiport --sports 631,515,9100,9101,9102,161,139,5353 -j ACCEPT 
        
     

        ## allow ping (a lot of services need ping)
        sudo iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT
        sudo iptables -A INPUT -p icmp --icmp-type echo-reply -j ACCEPT
        sudo iptables -A OUTPUT -p icmp --icmp-type echo-request -j ACCEPT
        sudo iptables -A OUTPUT -p icmp --icmp-type echo-reply -j ACCEPT

        if [ -f $IPSFILE ]; then
            for IP in `cat $IPSFILE`; do        #allow input and output for ALLOWEDIP
                echo "exception noticed $IP"
                IPPORTARRAY=(${IP//:/ })
                # destination - destinationports
                sudo iptables -A INPUT  -p tcp -d ${IPPORTARRAY[0]} -m multiport --dports ${IPPORTARRAY[1]},11411 -j ACCEPT
                sudo iptables -A OUTPUT  -p tcp -d ${IPPORTARRAY[0]} -m multiport --dports ${IPPORTARRAY[1]},11411 -j ACCEPT

                # source - destinationports
                sudo iptables -A INPUT  -p tcp -s ${IPPORTARRAY[0]} -m multiport --dports ${IPPORTARRAY[1]},11411 -j ACCEPT
                sudo iptables -A OUTPUT  -p tcp -s ${IPPORTARRAY[0]} -m multiport --dports ${IPPORTARRAY[1]},11411 -j ACCEPT

                # destination - sourceports
                sudo iptables -A INPUT  -p tcp -d ${IPPORTARRAY[0]} -m multiport --sports ${IPPORTARRAY[1]},11411 -j ACCEPT
                sudo iptables -A OUTPUT  -p tcp -d ${IPPORTARRAY[0]} -m multiport --sports ${IPPORTARRAY[1]},11411 -j ACCEPT

                # source - sourceports
                sudo iptables -A INPUT  -p tcp -s ${IPPORTARRAY[0]} -m multiport --sports ${IPPORTARRAY[1]},11411 -j ACCEPT
                sudo iptables -A OUTPUT  -p tcp -s ${IPPORTARRAY[0]} -m multiport --sports ${IPPORTARRAY[1]},11411 -j ACCEPT

            done
        fi
        sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT         #allow ESTABLISHED and RELATED (important for active server communication)
        sudo iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT
        #sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT  # castrated VPS

        #needed for multicast (twisted)  Multicast Address for Address Allocation for Private Internets
        sudo iptables -A INPUT -p udp -d 228.0.0.5/4 --dport 8005 -j ACCEPT
        sudo iptables -A OUTPUT -p udp -d 228.0.0.5/4 --dport 8005 -j ACCEPT
      
        #rules needed for geogebra 6 - chrome-app and geogebra-classic 
            # forget it - use geogebrajail.sh - as long as geogebra believes it has 
            # an internet connection it will try to connect to hundreds of google services and then timeout
  
        
        sleep 1
        #use reject (send errormsg) instead of drop to prevent timeouts of different programs that wait for an answer
#         sudo iptables -P INPUT DROP         #drop the rest
#         sudo iptables -P OUTPUT DROP
            
        sudo iptables -A INPUT -p udp  -j REJECT
        sudo iptables -A OUTPUT -p udp -j REJECT
        sudo iptables -A INPUT -p tcp -j REJECT --reject-with tcp-reset
        sudo iptables -A OUTPUT -p tcp -j REJECT --reject-with tcp-reset

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





if [ "$1" = "start" ]; then
    echo "starting firewall"
    stopIPtables
    
    #renew arp table before blocking everything
    myip=$(hostname -I)
    myiprange="${myip%.*}.0/24"
    sudo nmap -sn ${myiprange}   #we only scan the last 256 addresses asuming the teacher is in the same subnet as the students

    setIPtables
elif [ "$1" = "stop" ]; then
    echo "stopping firewall"
    stopIPtables
fi

