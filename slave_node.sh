#!/usr/bin/env bash

# Update package information and install required libraries
sudo apt-get update
sudo apt-get install -y libncurses5 libclass-methodmaker-perl

# Create necessary directories
sudo mkdir -p /opt/mysqlcluster/home
sudo mkdir -p /var/lib/mysqlcluster

# Change to the MySQL Cluster home directory
cd /opt/mysqlcluster/home

# Download and install MySQL Cluster Community Data Node
wget --progress=bar:force:noscroll https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb

# Display a message indicating successful installation
echo "MySQL Cluster Community Data Node installed successfully."
