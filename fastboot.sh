#!/bin/bash

# initial 
apt update
apt install git

# clone ibtc
git clone https://github.com/wuchanghui5220/ibtc.git

# install docker
curl -fsSL https://get.docker.com -o get-docker.sh
bash get-docker.sh

# pull and run ipsec
docker run --name ipsec-vpn-server --restart=always -v ikev2-vpn-data:/etc/ipsec.d -v /lib/modules:/lib/modules:ro -p 500:500/udp -p 4500:4500/udp -d --privileged hwdsl2/ipsec-vpn-server
# download vpnclient config 
echo "waiting for 5 second!"
sleep 5
echo "Copy vpnclient.mobileconfig "
docker cp ipsec-vpn-server:/etc/ipsec.d/vpnclient.mobileconfig ./
echo "Copy vpnclient.sswan "
docker cp ipsec-vpn-server:/etc/ipsec.d/vpnclient.sswan ./
echo ""
sleep 1
echo "Copy files to /home/admin/"
echo "# cp ./vpnclient.* /home/admin/"
cp ./vpnclient.* /home/admin/
echo ""
sleep 1
echo "Set file owner "
echo "# chown -R admin:admin /home/admin/vpnclient.*"
chown -R admin:admin /home/admin/vpnclient.*
echo ""
sleep 1
echo "check files!"
echo "# ls -lh /home/admin/vpnclient.*"
ls -lh /home/admin/vpnclient.*

echo ""
echo "Done! Enjoy!"

