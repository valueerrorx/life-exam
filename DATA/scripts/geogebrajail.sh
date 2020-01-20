#!/bin/bash
# geogebra needs a netjail otherwise it loads reeeeeeally slow or not at all

#logname seems to always deliver the current xsession user - no matter if you are using SUDO
USER=$(logname)   
HOME="/home/${USER}/"


sudo ip netns add jail
sudo ip netns exec jail su ${USER} -c 'google-chrome --app=http://localhost/.GeoGebra'
