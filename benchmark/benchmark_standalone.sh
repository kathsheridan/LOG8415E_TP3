#!/usr/bin/env bash
set -x

# Update package list and install MySQL Server and Sysbench
apt-get update && apt-get install -y mysql-server sysbench

# Create MySQL user and grant privileges
mysql -u root --password=mysql -e "CREATE USER 'user0'@'%' IDENTIFIED BY 'mysql';"
mysql -u root --password=mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'user0'@'%' WITH GRANT OPTION;"
mysql -u root --password=mysql -e "FLUSH PRIVILEGES;"

# Create a test database
mysql -u user0 --password=mysql -e "CREATE DATABASE DBTEST;"

echo "Preparing benchmark"
sysbench oltp_read_write --table-size=1000000 --mysql-db=DBTEST --mysql-user=user0 --mysql-password=mysql prepare

echo "Running benchmark (saving output to standalone_benchmark_results.txt)"
sysbench oltp_read_write --table-size=1000000 --threads=6 --time=60 --max-requests=0 --mysql-db=DBTEST --mysql-user=user0 --mysql-password=mysql run > standalone_benchmark_results.txt

echo "Benchmark complete"
