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

# install docker
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed, installing now..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  bash get-docker.sh
else
  echo "Docker is already installed"
fi


user="admin"
user_home="/home/$user"
html_dir="$user_home/html"
mail="wuchanghui5220@gmail.com"
website="nvlink.vip"

conf_dir="$user_home/nginx.conf"
certs_dir="$user_home/certs"


# check html directory
if [ ! -d "$html_dir" ]; then
  echo "$html_dir does not exist, creating it..."
  echo "# mkdir -p $html_dir"
  mkdir -p "$html_dir"
  echo "# chown -R $user:$user $html_dir"
  chown -R $user:$user $html_dir
fi

# check certs directory
if [ ! -d "$certs_dir" ]; then
  echo "$certs_dir does not exist, creating it..."
  echo "# mkdir -p $certs_dir"
  mkdir -p "$certs_dir"
  echo "# chown -R $user:$user $certs_dir"
  chown -R $user:$user $certs_dir
fi

# download acme.sh and install
echo " download acme.sh and install"
#curl https://get.acme.sh | sh -s email="$mail"

# retry times
MAX_RETRIES=3 

# default 
retries=1

# download and install acme.sh
install_acme() {
  curl https://get.acme.sh | sh -s email="$mail" 
  return $?
}

until install_acme || [ $retries -eq $MAX_RETRIES ]; do  
  echo "acme.sh安装失败,重试中..."
  retries=$(($retries+1)) 
  sleep 5
done  

# if retry over max retry, exit install
if [ $retries -eq $MAX_RETRIES ]; then
  echo "重试安装acme.sh失败,请检查网络或手动安装"
  exit 1
fi

# create alias
echo "alias acme.sh=~/.acme.sh/acme.sh" >> ~/.bashrc

source ~/.bashrc

# generate certificate
echo "generate certificate"
acme.sh --issue -d "$website" -d --webroot "$html_dir"

# install certificate
echo "install certificate"
acme.sh --install-cert -d "$website" --key-file $certs_dir/key.pem --fullchain-file $certs_dir/cert.pem 

# generate nginx config 
echo " generate nginx config "
cat <<EOF > nginx.conf
server {
    listen 80;
    listen [::]:80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
    }

    # other configurations...
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name localhost;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
    }

    # other configurations...
}
EOF

# copy nginx.conf to /home/admin
echo "cp nginx.conf $user_home"
cp nginx.conf $user_home



# pull and run nginx container
echo "pull and run nginx container"
if ! docker ps -a | grep -q nginx; then
  echo "nginx container not exists, creating..."
  echo "# docker pull nginx"
  docker pull nginx
  echo "Start nginx container"
  echo "# docker run -d --name nginx -p 80:80 -v /home/admin/html:/usr/share/nginx/html nginx"
  docker run -d --name nginx --restart=always -p 80:80 -p 443:443 -v $conf_dir:/etc/nginx/conf.d/default.conf -v $certs_dir:/etc/nginx/certs -v $html_dir:/usr/share/nginx/html nginx
else
  echo "Nginx container already exists"  
fi

# Initial HTML root directory
echo "Copying files to $html_dir"
echo "# cp favicon.ico index.html $html_dir"
cp ./web_file/* $html_dir

# Copying Python files to $user_home
python_files="fw_link_data.py fwlink.py ibtc2.py ofed.py"
logo_pics="zy_elite.png"
echo "# cp $python_files $logo_pics $user_home"
cp $python_files $logo_pics $user_home
echo "Set Python file  permissions"
echo "# chown -R $user:$user $user_home"
chown -R $user:$user $user_home
echo "# chmod +x $user_home/*.py"
chmod +x $user_home/*.py
echo ""
echo "# ls -lh $user_home"
ls -lh $user_home
echo ""
echo "Done! Enjoy!"
