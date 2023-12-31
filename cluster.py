import sys
import time
import boto3
import paramiko
import subprocess
from ec2_instances import *
from security_groups import *


def main():
    # Aws credentials
    aws_access_key_id = "ASIAXEOTBFHD3YM3GW7K"
    aws_secret_access_key = "nUeGrQcBKB+AfdBH+FZjhX3kpzOjWRUUEin08bCU"
    aws_session_token = "FwoGZXIvYXdzEID//////////wEaDCqG5haS6+QS2p8xXiKCAWfIl6f8EbwpSOqFRNyj9IfvbI8SEClId7FXfaCPTsqkHzPcF3XUI49iUTM9368JGzInJj3PzNI4ptqjggHIOmtvpVibYNc+y5h7dQxDclJcWgSZG0FMefRZr785wVzucFmUMdPIfhG1xRi4LlYt3q6lIDZJ5A+Sd1nIB3V3cUayhjIo/7DCrAYyKERdR2yr3x2ldKF6OyWNQc0euhgpFO2MonDxmWWy9UyFj7bciUKCk5U="

    subnet_id = str(sys.argv[1])

    ec2_client = boto3.client('ec2',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token,
                              region_name='us-east-1'
                              )

    ec2_resource = boto3.resource('ec2',
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  aws_session_token=aws_session_token,
                                  region_name='us-east-1'
                                  )

    # maybe not hardcode eventually
    vpc_id = "vpc-077c45ea8fc1c9a3a"
    subnet_id = "subnet-0b97d50123de50790"

    # security group
    security_group = create_standalone_group(ec2_client, "cluster_group", vpc_id)
    time.sleep(10)

    # ec2 cluster
    master_node = create_cluster_instance(ec2_resource, "172.31.17.1", security_group['GroupId'], open(
        'master_node.sh').read(), "Master-Node", subnet_id)
    slave_node1 = create_cluster_instance(ec2_resource, "172.31.17.2", security_group['GroupId'], open(
        'slave_node.sh').read(), "Slave-Node1", subnet_id)
    slave_node2 = create_cluster_instance(ec2_resource, "172.31.17.3", security_group['GroupId'], open(
        'slave_node.sh').read(), "Slave-Node2", subnet_id)
    slave_node3 = create_cluster_instance(ec2_resource, "172.31.17.4", security_group['GroupId'], open(
        'slave_node.sh').read(), "Slave-Node3", subnet_id)
    print("Waiting for instance to pass checks")
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[master_node[0].id])
    waiter.wait(InstanceIds=[slave_node1[0].id])
    waiter.wait(InstanceIds=[slave_node2[0].id])
    waiter.wait(InstanceIds=[slave_node3[0].id])

    # public ip
    reservations = ec2_client.describe_instances(InstanceIds=[master_node[0].id])['Reservations']
    ip = reservations[0]["Instances"][0].get('PublicIpAddress')

    time.sleep(60)

    key = paramiko.RSAKey.from_private_key_file("tp3key.pem")
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSHClient.connect(ip, username='ubuntu', pkey=key)

    print("Checking cluster status... ")
    # Check MySQL Cluster status
    mysql_cluster_status = check_mysql_cluster_status(SSHClient)
    print(f"MySQL Cluster Status: {mysql_cluster_status}")

    print("~~ MySQL Cluster Benchmark~~")

    print('Connected to: ' + str(ip))

    commands = [
        "sudo systemctl start mysqld > error_log.log 2>&1"
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password=ClusterPassword --mysql_storage_engine=ndbcluster prepare",
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password=ClusterPassword --mysql_storage_engine=ndbcluster --num-threads=6 --max-time=60 --max-requests=0 run > cluster_benchmark_results.txt",
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password=ClusterPassword --mysql_storage_engine=ndbcluster cleanup"
    ]
    for command in commands:
        stdin, stdout, stderr = SSHClient.exec_command(command)
        print(stdout.read())
        print(stderr.read())

    print("Logging benchmark results")
    subprocess.call(['scp', '-o','StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-i', 'tp3key.pem', "ubuntu@" + str(ip) + ":cluster_benchmark_results.txt", '.'])


    destroy = False
    while destroy == False:
        answer = input("Terminate cluster? (Type Yes) : ")
        if answer == "Yes":
            print("Terminating cluster")
            terminate_instance(ec2_client, [master_node[0].id])
            terminate_instance(ec2_client, [slave_node1[0].id])
            terminate_instance(ec2_client, [slave_node2[0].id])
            terminate_instance(ec2_client, [slave_node3[0].id])
            print("Waiting to delete security group")
            time.sleep(60)
            print("Deleting security group")
            delete_security_group(ec2_client, security_group['GroupId'])
            destroy = True
        else:
            continue

if __name__ == "__main__":
    main()