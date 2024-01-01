#!/usr/bin/env bash
set -x

apt --fix-broken -y install
apt-get install -y sysbench
mysql -u user0 --password=mysql -e "CREATE DATABASE DBTEST;"

echo "Preparing benchmark..."
sysbench oltp_read_write --table-size=1000000 --mysql-db=DBTEST --mysql-user=user0 --mysql-password=mysql prepare
echo "Running benchmark (saving output to output_benchmark_cluster.txt)..."
sysbench oltp_read_write --table-size=1000000 --threads=6 --time=60 --max-requests=0 --mysql-db=DBTEST --mysql-user=user0 --mysql-password=mysql run > output_benchmark_cluster.txt
echo "Benchmark done !"
