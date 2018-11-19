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
        sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT     #allow DNS
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

        #rules needed for geogebra 6 - chrome-app and geogebra-classic 
            # forget it - use geogebrajail.sh - as long as geogebra believes it has 
            # an internet connection it will try to connect to hundreds of google services and then timeout
  
        
        sleep 1
        #use reject (send errormsg) instead of drop to prevent timeouts of different programs that wait for an answer
        sudo iptables -P INPUT REJECT          #drop the rest
        sudo iptables -P OUTPUT REJECT
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
    sleep 1
    setIPtables
elif [ "$1" = "stop" ]; then
    echo "stopping firewall"
    stopIPtables
fi

