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

# We need to delete the instance afetr
def terminate_instance(client, id):
    print('Instance to terminate :')
    print(id)
    client.terminate_instances(InstanceIds=(id))