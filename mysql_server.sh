#!/usr/bin/env bash
set -e -x

wget --progress=bar:force:noscroll https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.0/mysql-cluster_8.0.31-1ubuntu20.04_amd64.deb-bundle.tar
mkdir install
tar -xvf mysql-cluster_8.0.31-1ubuntu20.04_amd64.deb-bundle.tar -C install/
cd install && \
    sudo dpkg -i *.deb && \
    sudo apt-get install -y -f
sudo systemctl start mysql
sleep 1
sudo mysql -u root --password=mysql -e "CREATE USER 'user0'@'%' IDENTIFIED BY 'mysql';"
sudo mysql -u root --password=mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'user0'@'%' WITH GRANT OPTION;"
sudo mysql -u root --password=mysql -e "FLUSH PRIVILEGES;"
sleep 3 && sudo systemctl restart mysql && sleep 3
sudo mkdir -p /opt/mysqlcluster/deploy/conf /opt/mysqlcluster/deploy/ndb_data /opt/mysqlcluster/deploy/mysqld_data /var/lib/mysqlcluster && \
                                                    sudo cp /home/ubuntu/config.ini /opt/mysqlcluster/deploy/conf/ && \
                                                    sudo ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/ && \
sleep 1
sudo bash -c 'cat /home/ubuntu/server_conf.conf >> /etc/mysql/my.cnf'


wget --progress=bar:force:noscroll https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xvf sakila-db.tar.gz
echo "Installing Sakila..."
mysql -u user0 --password=mysql -e "SOURCE sakila-db/sakila-schema.sql"
mysql -u user0 --password=mysql -e "SOURCE sakila-db/sakila-data.sql"
systemctl status mysql

