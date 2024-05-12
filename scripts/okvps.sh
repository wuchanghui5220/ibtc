#!/bin/bash

# 更新软件源并安装必要的软件包
sudo apt-get update
sudo apt-get install -y git cron

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo bash get-docker.sh

# 部署IPsec VPN服务器Docker容器
sudo docker run \
    --name ipsec-vpn-server \
    --restart=always \
    -v ikev2-vpn-data:/etc/ipsec.d \
    -v /lib/modules:/lib/modules:ro \
    -p 500:500/udp \
    -p 4500:4500/udp \
    -d --privileged \
    hwdsl2/ipsec-vpn-server

# 安装Python3和pip
sudo apt-get install -y python3-pip

# 安装Playwright和相关依赖项
sudo apt-get install -y nodejs npm
sudo npm install -g playwright
sudo npx playwright install-deps
playwright install

# 安装networkx和matplotlib
pip3 install --user networkx matplotlib

# 克隆GitHub仓库
git clone https://github.com/wuchanghui5220/ibtc.git

# 拉取并运行Nginx Docker容器
sudo docker pull nginx
sudo docker run -d \
    --name nginx \
    --restart=always \
    -p 80:80 \
    -v /home/admin/ibtc/html:/usr/share/nginx/html \
    nginx

# 安装和配置SSL证书
curl https://get.acme.sh | sh -s email=wuchanghui5220@gmail.com
echo "alias acme.sh=~/.acme.sh/acme.sh" >> ~/.bashrc
source ~/.bashrc
acme.sh --issue -d nvlink.vip --webroot /home/admin/ibtc/html/
acme.sh --install-cert -d nvlink.vip \
    --key-file /home/admin/ibtc/html/certs/key.pem \
    --fullchain-file /home/admin/ibtc/html/certs/cert.pem

# 配置并重新启动Nginx容器
sudo docker stop nginx
sudo docker rm nginx
sudo docker run -d \
    --name nginx \
    --restart=always \
    -p 80:80 \
    -p 443:443 \
    -v /home/admin/ibtc/html/nginx.conf:/etc/nginx/conf.d/default.conf \
    -v /home/admin/ibtc/html/certs:/etc/nginx/certs \
    -v /home/admin/ibtc/html:/usr/share/nginx/html \
    nginx
