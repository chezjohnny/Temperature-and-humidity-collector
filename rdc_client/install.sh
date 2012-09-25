#!/bash
echo "Install client python script"
python setup.py install
echo "Install rc scripts"
cp system/rc/rc.local /etc/.

mkdir -p /var/log/rdcecho "Install network conf"
mkdir -p /var/log/rdc
cp system/ppp/interfaces /etc/network/

echo "Install ppp scripts"
cp system/ppp/peers/mbudget /etc/ppp/peers/
cp system/ppp/peers/options /etc/ppp/.
cp system/ppp/ntpdate /etc/ppp/ip-up.d/.
cp system/ppp/rdcc-up /etc/ppp/ip-up.d/.
cp system/ppp/rdcc-down /etc/ppp/ip-down.d/.
cp system/ppp/pct-hsdpa-3g-huawei-e220-mbudget.chat /etc/chatscripts/.

echo "Install udev scripts"
cp system/udev/* /lib/udev/rules.d/.

