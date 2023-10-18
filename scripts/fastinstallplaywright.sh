#!/bin/bash

# install python3 and pip playwright
sudo apt update
sudo apt install -y python3-pip nodejs npm
sudo npm install -g playwright
pip install --break-system-packages playwright tqdm

# install networkx matplotlib
pip install --user networkx matplotlib --break-system-packages

# Use admin to install following packages if you want to run the Script for user admin 
playwright install
sudo playwright install-deps
