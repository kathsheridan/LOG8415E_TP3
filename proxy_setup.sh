#!/bin/bash

# Update and install necessary packages
sudo apt update
sudo apt install python3-pip -y

# Install Python packages using pip
sudo pip install sshtunnel pythonping pymysql
