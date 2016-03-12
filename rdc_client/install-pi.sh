#!/bin/bash

echo "Install Dependencies"
sudo apt-get install ppp wvdial vim git owfs-common virtualenvwrapper usb-modeswitch

echo "Install client python script"
source $VIRTUALENVWRAPPER_SCRIPT 
mkvirtualenv --system-site-packages rdc
pip install -e .
cp cfg/config.yaml /home/pi/.virtualenvs/rdc/config.yaml


echo "Install config files"
sudo cp system/pi/ppp0.service /etc/systemd/system/.
sudo cp system/pi/10-* /lib/udev/rules.d/.
sudo cp system/pi/wvdial.conf /etc/.
sudo cp system/pi/options /etc/ppp/.
sudo cp system/pi/rdcc-up /etc/ppp/ip-up.d/,
sudo cp system/pi/rdcc-down /etc/ppp/ip-down.d/.
sudo cp system/pi/rc.local /etc/. 
