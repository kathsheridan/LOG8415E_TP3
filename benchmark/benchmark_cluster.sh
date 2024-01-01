#!/usr/bin/env bash
set -x

# Fix broken dependencies
apt --fix-broken -y install

# Install sysbench
apt-get install -y sysbench

# Create a test database
mysql -u user0 --password=mysql -e "CREATE DATABASE DBTEST;"

echo "Preparing benchmark"
# Prepare the sysbench OLTP read-write benchmark
sysbench oltp_read_write --table-size=1000000 --mysql-db=DBTEST --mysql-user=user0 --mysql-password=mysql prepare

echo "Running benchmark (saving output to cluster_benchmark_results.txt)"
# Run the sysbench OLTP read-write benchmark
sysbench oltp_read_write --table-size=1000000 --threads=6 --time=60 --max-requests=0 --mysql-db=DBTEST --mysql-user=user0 --mysql-password=mysql run > cluster_benchmark_results.txt

echo "Benchmark complete"
