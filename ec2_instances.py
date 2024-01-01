import boto3
from botocore.exceptions import ClientError
from os import path
import constants

EC2_RESOURCE = boto3.resource('ec2')
EC2_CLIENT = boto3.client('ec2')


def create_ec2(instance_type, sg_id, key_name, user_data):
    # Create an EC2 instance
    instance = EC2_RESOURCE.create_instances(
        ImageId='ami-0149b2da6ceec4bb0',
        MinCount=1,
        MaxCount=1,
        UserData=user_data,
        InstanceType=instance_type,
        Monitoring={'Enabled': True},
        SecurityGroupIds=[sg_id],
        KeyName=key_name,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'projet-instance'
                    },
                ]
            },
        ]
    )[0]
    print(f'{instance} is starting')
    return instance


def create_security_group():
    # Create a security group
    sec_group_name = 'lab2-security-group'
    security_group_id = None
    try:
        response = EC2_CLIENT.create_security_group(
            GroupName=sec_group_name,
            Description='Security group for the ec2 instances used in Lab1'
        )
        security_group_id = response['GroupId']
        print(f'Successfully created security group {security_group_id}')
        sec_group_rules = [
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
             {'IpProtocol': 'tcp',
             'FromPort': 1186,
             'ToPort': 1186,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
        data = EC2_CLIENT.authorize_security_group_ingress(GroupId=security_group_id,
                                                           IpPermissions=sec_group_rules)
        print(f'Successfully updated security group rules with : {sec_group_rules}')
        return security_group_id
    except ClientError as e:
        try:
            response = EC2_CLIENT.describe_security_groups(
                Filters=[
                    dict(Name='group-name', Values=[sec_group_name])
                ])
            security_group_id = response['SecurityGroups'][0]['GroupId']
            print(f'Security group already exists with id {security_group_id}.')
            return security_group_id
        except ClientError as e:
            print(e)
            exit(1)


def create_private_key_filename(key_name):
    # Generate a filename to save the key pair
    return f'./private_key_{key_name}.pem'


def create_key_pair(key_name, private_key_filename):
    # Generate a key pair to access the instance
    response = EC2_CLIENT.describe_key_pairs()
    kp = [kp for kp in response['KeyPairs'] if kp['KeyName'] == key_name]
    if len(kp) > 0 and not path.exists(private_key_filename):
        print(f'{key_name} already exists distantly, but the private key file has not been downloaded. Either delete the remote key or download the associate private key as {private_key_filename}.')
        exit(1)

    print(f'Creating {private_key_filename}')
    if path.exists(private_key_filename):
        print(f'Private key {private_key_filename} already exists, using this file.')
        return

    response = EC2_CLIENT.create_key_pair(KeyName=key_name)
    with open(private_key_filename, 'w+') as f:
        f.write(response['KeyMaterial'])
    print(f'{private_key_filename} written.')


def retrieve_instance_ip_dns(instance_id):
    # Retrieve an instance's public IP
    print(f'Retrieving instance {instance_id} public IP...')
    instance_config = EC2_CLIENT.describe_instances(InstanceIds=[instance_id])
    instance_ip = instance_config["Reservations"][0]['Instances'][0]['PublicIpAddress']
    instance_dns_name = instance_config["Reservations"][0]['Instances'][0]['PrivateDnsName']
    print(f'Public IP : {instance_ip}, Private DNS : {instance_dns_name}')
    return instance_ip, instance_dns_name


def start_instance(user_data):
    # Start an instance with the lab2 configuration
    instance = create_ec2('t2.micro', sg_id, key_name, user_data)
    print(f'Waiting for instance {instance.id} to be running...')
    instance.wait_until_running()
    instance_ip, instance_dns_name = retrieve_instance_ip_dns(instance.id)
    print(f'Instance {instance.id} started. Access it with \'ssh -i {private_key_filename} ubuntu@{instance_ip}\'')
    return instance_ip, instance_dns_name

def generate_cluster_config_file(instance_infos):
    # Generate configuration files for the cluster
    template_master = constants.TEMPLATE_MASTER
    template_slave = constants.TEMPLATE_SLAVE
    template_sql_server = constants.TEMPLATE_SQL_SERVER

    with open('master_node/config.ini', 'w+') as f:
        f.write(template_master.format(manager_hostname=instance_infos[0]['dns'],
                                       slave_0_hostname=instance_infos[1]['dns'],
                                       slave_1_hostname=instance_infos[2]['dns'],
                                       slave_2_hostname=instance_infos[3]['dns']))
    with open('master_node/my.cnf', 'w+') as f:
        f.write(template_slave.format(manager_hostname=instance_infos[0]['dns']))
    with open('master_node/server_conf.conf', 'w+') as f:
        f.write(template_sql_server.format(manager_hostname=instance_infos[0]['dns']))

def generate_proxy_py(instance_infos):
    # Generate the proxy python file used for the proxy cloud pattern
    with open('template_proxy.py', 'r') as f:
        lines = f.read()
    formatted_lines = lines.replace('_MASTER_HOSTNAME_PLACEHOLDER_', instance_infos[0]['ip']) \
                            .replace("_SLAVE_1_HOSTNAME_PLACEHOLDER_", instance_infos[1]['ip']) \
                            .replace("_SLAVE_2_HOSTNAME_PLACEHOLDER_", instance_infos[2]['ip']) \
                            .replace("_SLAVE_3_HOSTNAME_PLACEHOLDER_", instance_infos[3]['ip'])
    with open('app.py', 'w+') as f_api:
        f_api.write(formatted_lines)
    print("Wrote api to app.py")

if __name__ == "__main__":
    key_name = 'PROJET_KEY'
    private_key_filename = create_private_key_filename(key_name)
    create_key_pair(key_name, private_key_filename)

    sg_id = create_security_group()

    instance_infos = []
    user_data = ""
    for i in range(6):
        if i == 4:
            user_data = constants.USER_DATA_PROXY
        instance_ip, instance_dns_name = start_instance(user_data)
        instance_infos.append({'ip': instance_ip, 'dns': instance_dns_name})

    with open('environment_vars.txt', 'w+') as f:
        for idx, instance_info in enumerate(instance_infos):
            if idx == 0:
                f.write(f'INSTANCE_IP_MASTER_IP={instance_info["ip"]}\n')
                f.write(f'INSTANCE_IP_MASTER_DNS={instance_info["dns"]}\n')
            elif idx == len(instance_infos) - 2:
                f.write(f'INSTANCE_IP_PROXY_IP={instance_info["ip"]}\n')
                f.write(f'INSTANCE_IP_PROXY_DNS={instance_info["dns"]}\n')
            elif idx == len(instance_infos) - 1:
                f.write(f'INSTANCE_IP_STANDALONE_IP={instance_info["ip"]}\n')
                f.write(f'INSTANCE_IP_STANDALONE_DNS={instance_info["dns"]}\n')
            else:
                f.write(f'INSTANCE_IP_CHILD_IP_{idx-1}={instance_info["ip"]}\n')
                f.write(f'INSTANCE_IP_CHILD_DNS_{idx-1}={instance_info["dns"]}\n')
        f.write(f'PRIVATE_KEY_FILE={private_key_filename}\n')
    print('Wrote instance\'s IP and private key filename to environment_vars.txt')

    generate_cluster_config_file(instance_infos)
    generate_proxy_py(instance_infos)
