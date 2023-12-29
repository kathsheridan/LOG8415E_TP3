import boto3
import time
import paramiko

import subprocess
from ec2_instances import *
from security_groups import *

def main():
    # Aws credentials
    aws_access_key_id = "ASIAXEOTBFHDQIG6Z5MF"
    aws_secret_access_key = "asy2/aGfvAboPByoOK2T7Mps9U/uxQdqYLZTYrMi"
    aws_session_token = "FwoGZXIvYXdzEGcaDAoNu9qU7R/ODPv4GSKCAaQSBcvA7VUMxHfXwaNmqOq62Isuc/CVQ1rqZ8MH9jBBi0w4NDSL8H1JS8oVe0w1XBv06VlmNNu8vRbYMBci7SNdVKsYo7shV84BntvKvDguP8w+lZQ1nV9IzKOUs1LDL2QHYD3P6U986FF+r4zD+92Ud4kQ4PV+7dmsovFt6o4K1UsolfC8rAYyKIPMBbfb4m2B3nNcettharGNjTfFQIePuRlN8x4ug9W/EHpEvjmvTKs="

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
    security_group = create_standalone_group(ec2_client, "standalone_group", vpc_id)
    time.sleep(10)

    # EC2 instance
    instance = create_standalone_instance(ec2_resource, security_group['GroupId'], subnet_id)
    print("Waiting for instance to pass checks")
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instance[0].id])

    # public ip
    reservations = ec2_client.describe_instances(InstanceIds=[instance[0].id])['Reservations']
    ip = reservations[0]["Instances"][0].get('PublicIpAddress')

    time.sleep(120)
    print("~~ MySQL Standalone Benchmark~~")
    key = paramiko.RSAKey.from_private_key_file("tp3key.pem")
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    SSHClient.connect(ip, username='ubuntu', pkey=key)
    print('Connected to : ' + str(ip))

    commands = [
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root prepare",
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --num-threads=6 --max-time=60 --max-requests=0 run > standalone_benchmark_results.txt",
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root cleanup"
    ]
    for command in commands:
        stdin, stdout, stderr = SSHClient.exec_command(command)
        print(stdout.read())
        print(stderr.read())

    print("Logging benchmark results")
    subprocess.call(['scp', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-i', 'tp3key.pem', "ubuntu@" + str(ip) + ":standalone_benchmark_results.txt", '.'])
    print("Terminating instance")
    terminate_instance(ec2_client, [instance[0].id])
    print("Waiting to delete security group")
    time.sleep(120)
    print("Deleting security group")
    delete_security_group(ec2_client, security_group['GroupId'])

if __name__ == "__main__":
    main()

