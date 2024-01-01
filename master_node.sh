#!/usr/bin/env bash

# Update package information and install required libraries
sudo apt-get update
sudo apt-get install -y libncurses5 libaio1 libmecab2

# Create necessary directories
sudo mkdir -p /opt/mysqlcluster/home
sudo mkdir -p /var/lib/mysqlcluster

# Download and install MySQL Cluster Management Server
wget --progress=bar:force:noscroll https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb

# Download MySQL Cluster
wget --progress=bar:force:noscroll http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
tar -xf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz

# Move MySQL Cluster to a dedicated directory
mv mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

# Add an alias for ndb_mgm to the user's profile
echo "alias ndb_mgm=/home/ubuntu/mysqlc/bin/ndb_mgm" >> /home/ubuntu/.profile

# Display a message indicating successful setup
echo "MySQL Cluster Management Server and MySQL Cluster setup completed."
