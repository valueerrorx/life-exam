#!/bin/bash
# geogebra needs a netjail otherwise it loads reeeeeeally slow

USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO
HOME="/home/${USER}/"


sudo ip netns add jail
sudo ip netns exec jail su ${USER} -c geogebra-classic

