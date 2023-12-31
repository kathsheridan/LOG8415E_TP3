# Standalone T2 MICRO instance
def create_standalone_instance(ec2, securityGroup, subnet_id):
    instance = ec2.create_instances(
        ImageId="ami-0574da719dca65348",
        InstanceType="t2.micro",
        KeyName="tp3key",
        UserData=open('standalone.sh').read(),
        SubnetId=subnet_id,
        SecurityGroupIds=[
            securityGroup
        ],
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'MYSQL Standalone'
                },
            ]
        },
    ]
)
    print(f"Instance {instance[0].id} created successfully.")
    return instance

# Cluster T2 MICRO instance
def create_cluster_instance(ec2, ip_address, securityGroup, userdata, instance_name, subnet_id):
    instance = ec2.create_instances(
        ImageId="ami-0574da719dca65348",
        InstanceType="t2.micro",
        KeyName="tp3key",
        UserData=userdata,
        PrivateIpAddress=ip_address,
        SubnetId=subnet_id,
        SecurityGroupIds=[
            securityGroup
        ],
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': instance_name
                },
            ]
        },
        ]
        )

    return instance
def check_mysql_cluster_status(ssh_client):
    commands = [
        "sudo systemctl status ndb_mgmd",
        "sudo systemctl status ndbd",
        "sudo systemctl status mysqld",
        "sudo ndb_mgm -e 'show'",
        "sudo ndb_mgm -e 'all report memory'"
    ]

    status_info = {}
    for command in commands:
        try:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8')
            status_info[command] = output
        except Exception as e:
            status_info[command] = f"Error occurred: {str(e)}"

    return status_info



# Proxy T2 LARGE instance
def create_proxy_instance(ec2, ip_address, securityGroup, subnet_id):
    instance = ec2.create_instances(
        ImageId="ami-0574da719dca65348",
        InstanceType="t2.large",
        KeyName="tp3key",
        UserData=open('proxy_setup.sh').read(),
        PrivateIpAddress=ip_address,
        SubnetId=subnet_id,
        SecurityGroupIds=[
            securityGroup
        ],
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': "proxy"
                },
            ]
        },
        ]
        )

    return instance

# We need to delete the instance afetr
def terminate_instance(client, id):
    print('Instance to terminate :')
    print(id)
    client.terminate_instances(InstanceIds=(id))