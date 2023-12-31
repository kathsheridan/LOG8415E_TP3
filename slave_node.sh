#!/bin/bash

# Update and install necessary packages
sudo apt update
sudo apt install libclass-methodmaker-perl libncurses5 -y

# Download and install MySQL Cluster Data Node
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb

# Configure MySQL Cluster in my.cnf
echo "
[mysql_cluster]
ndb-connectstring=ip-172-31-17-1.ec2.internal
" | sudo tee -a /etc/my.cnf

# Create directory for MySQL Data Node
sudo mkdir -p /usr/local/mysql/data

# Configure MySQL Data Node as a systemd service
echo "
[Unit]
Description=MySQL NDB Data Node Daemon
After=network.target auditd.service

[Service]
Type=forking
ExecStart=/usr/sbin/ndbd
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
" | sudo tee -a /etc/systemd/system/ndbd.service

# Reload systemd, enable and start MySQL Data Node
sudo systemctl daemon-reload
sudo systemctl enable ndbd
sudo systemctl start ndbd
