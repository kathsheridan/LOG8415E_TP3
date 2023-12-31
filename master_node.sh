#!/bin/bash

# Update and install necessary packages
sudo apt update
sudo apt install libaio1 libmecab2 libncurses5 sysbench -y

# Download and install MySQL Cluster Management Server
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb

# Create directory for MySQL Cluster data
sudo mkdir /var/lib/mysql-cluster

# Configure MySQL Cluster
echo "
[ndbd default]
NoOfReplicas=3

[ndb_mgmd]
hostname=ip-172-31-17-1.ec2.internal
datadir=/var/lib/mysql-cluster
NodeId=1

[ndbd]
hostname=ip-172-31-17-2.ec2.internal
NodeId=2
datadir=/usr/local/mysql/data

[ndbd]
hostname=ip-172-31-17-3.ec2.internal
NodeId=3
datadir=/usr/local/mysql/data

[ndbd]
hostname=ip-172-31-17-4.ec2.internal
NodeId=4
datadir=/usr/local/mysql/data

[mysqld]
hostname=ip-172-31-17-1.ec2.internal
nodeid=50
" | sudo tee -a /var/lib/mysql-cluster/config.ini

# Configure MySQL Cluster Management Server as a systemd service
echo "
[Unit]
Description=MySQL NDB Cluster Management Server
After=network.target auditd.service

[Service]
Type=forking
ExecStart=/usr/sbin/ndb_mgmd -f /var/lib/mysql-cluster/config.ini
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
" | sudo tee -a /etc/systemd/system/ndb_mgmd.service

# Reload systemd, enable and start MySQL Cluster Management Server
sudo systemctl daemon-reload
sudo systemctl enable ndb_mgmd
sudo systemctl start ndb_mgmd

# Download and install MySQL Cluster components
wget https://dev.mysql
