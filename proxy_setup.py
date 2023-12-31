import subprocess
import sys
import time
import boto3
from ec2_instances import create_proxy_instance, terminate_instance
from security_groups import create_proxy_group, delete_security_group


def main():
    # Aws credentials
    aws_access_key_id = "ASIAXEOTBFHD4NDHELQR"
    aws_secret_access_key = "3UdmNSdEvuYpWTjsaGfdtPdq2TlmUiDUExBHtufL"
    aws_session_token = "FwoGZXIvYXdzEJP//////////wEaDOobPxJoT0qRjCCBdiKCAahzZKQFG8euNEyed12NirKFM2rhcAlfK3qxeW9Ue8dUhTmBe4xQg7rGu1UDXDXkjOdF2zHU+kHsHMrhKU3EzpZ4m5Dn6m8axVRlbwCN/4D0k8+8350Oy24SAfnsBWMMHr5YW2MRs2I8Lke0045lyNyRamsblvrZysVP4Udt/uLXNLMozcXGrAYyKIXL+X94G1m+Yfs5oQpAhtV9ocutjjXImM+IqcHk5ugaelrEHlC0Rm8="

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

    # Create security group
    security_group = create_proxy_group(ec2_client, "proxy_group", vpc_id)

    time.sleep(10)

    # Create EC2 instance
    instance = create_proxy_instance(ec2_resource, "172.31.17.5", security_group['GroupId'], subnet_id)

    print("Waiting for instance to pass checks")
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instance[0].id])

    time.sleep(60)

    print("Ready!")

    # Get public IP
    reservations = ec2_client.describe_instances(InstanceIds=[instance[0].id])['Reservations']
    ip = reservations[0]["Instances"][0].get('PublicIpAddress')

    print("Copying key to proxy...")
    subprocess.call(
        ['scp', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-i', 'tp3key.pem',
         'tp3key.pem', "ubuntu@" + str(ip) + ":tp3key.pem"])

    destroy = False
    while not destroy:
        answer = input("Terminate proxy? (Type Yes) : ")
        if answer == "Yes":
            print("Terminating instance")
            terminate_instance(ec2_client, [instance[0].id])
            print("Waiting to delete security group")
            time.sleep(60)
            print("Deleting security group")
            delete_security_group(ec2_client, security_group['GroupId'])
            destroy = True
        else:
            continue


if __name__ == "__main__":
    main()
