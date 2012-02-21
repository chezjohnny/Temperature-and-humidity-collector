apt-get install python-ow python-virtualenv pppd
apt-get install ntpdate
apt-get install ntp
apt-get install locales
pppd /dev/ttyUSB0 call mbudget nodetach
ifup ppp0
