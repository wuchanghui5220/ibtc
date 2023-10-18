#!/bin/bash

# initial 
if ! command -v git &> /dev/null
then
    echo "Git is not installed, installing now..."
    sudo apt update
    sudo apt install -y git
else
    echo "Git is already installed"
fi

# clone ibtc
# git clone https://github.com/wuchanghui5220/ibtc.git

# install docker
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed, installing now..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  bash get-docker.sh
else
  echo "Docker is already installed"
fi

# pull and run ipsec
# check ipsec-vpn-server
if ! docker ps -a | grep -q ipsec-vpn-server; then
  echo "ipsec-vpn-server container not exists, creating..."
  docker run --name ipsec-vpn-server --restart=always -v ikev2-vpn-data:/etc/ipsec.d -v /lib/modules:/lib/modules:ro -p 500:500/udp -p 4500:4500/udp -d --privileged hwdsl2/ipsec-vpn-server
else
  echo "ipsec-vpn-server container already exists"  
fi

user="admin"
user_home="/home/$user"
html_dir="$user_home/html"

# download vpnclient config 
echo "ipsec-vpn-server is booting, waiting for 3 second!"
sleep 3
echo "Copy vpnclient.mobileconfig "
docker cp ipsec-vpn-server:/etc/ipsec.d/vpnclient.mobileconfig ./
echo "Copy vpnclient.sswan "
docker cp ipsec-vpn-server:/etc/ipsec.d/vpnclient.sswan ./
echo ""
sleep 1
echo "Copy files to $user_home"
echo "# cp ./vpnclient.* $user_home"
cp ./vpnclient.* $user_home
echo ""
sleep 1
echo "Set file owner "
echo "# chown -R $user:$user $user_home/vpnclient.*"
chown -R $user:$user $user_home/vpnclient.*
echo ""
sleep 1
echo "check files!"
echo "# ls -lh $user_home/vpnclient.*"
ls -lh $user_home/vpnclient.*

echo ""
echo "Done! Enjoy!"

