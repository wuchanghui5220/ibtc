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
html_dir="$user_home/ibtc/html"

# check html directory
if [ ! -d "$html_dir" ]; then
  echo "$html_dir does not exist, creating it..."
  echo "# mkdir -p $html_dir"
  mkdir -p "$html_dir"
  echo "# chown -R $user:$user $html_dir"
  chown -R $user:$user $html_dir
fi

# pull and run nginx container
if ! docker ps -a | grep -q nginx; then
  echo "nginx container not exists, creating..."
  echo "# docker pull nginx"
  docker pull nginx
  echo "Start nginx container"
  echo "# docker run -d --name nginx -p 80:80 -v /home/admin/ibtc/html:/usr/share/nginx/html nginx"
  docker run -d --name nginx -p 80:80 -v /home/admin/ibtc/html:/usr/share/nginx/html nginx
else
  echo "Nginx container already exists"  
fi

# Initial HTML root directory
#echo "Copying files to $html_dir"
#echo "# cp favicon.ico index.html $html_dir"
#cp ./web_file/* $html_dir

# Copying Python files to $user_home
#python_files="fw_link_data.py fwlink.py ibtc2.py ofed.py"
#logo_pics="zy_elite.png"
#echo "# cp $python_files $logo_pics $user_home"
#cp $python_files $logo_pics $user_home
#echo "Set Python file  permissions"
#echo "# chown -R $user:$user $user_home"
chown -R $user:$user $user_home
echo "# chmod +x $html_dir/*.py"
chmod +x $html_dir/*.py
echo ""
echo "# ls -lh $html_dir"
ls -lh $html_dir
echo ""
echo "Done! Enjoy!"
