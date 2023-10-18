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
docker cp ipsec-vpn-server:/etc/ipsec.d/vpnclient.mobileconfig ./
docker cp ipsec-vpn-server:/etc/ipsec.d/vpnclient.sswan ./

chown -R admin:admin  vpnclient.* 
cp ./vpnclient.* /home/admin/

ls -lh /home/admin/vpnclient.*

echo "Done! Enjoy!"
