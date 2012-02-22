apt-get install python-ow python-virtualenv pppd
apt-get install ntpdate
apt-get install ntp
apt-get install locales
pppd /dev/ttyUSB0 call mbudget nodetach
ifup ppp0
To disable flash disk
echo 'AT^U2DIAG=0^M' > /dev/ttyUSB2
To disable report
echo 'AT^CURC=0^M' > /dev/ttyUSB2
