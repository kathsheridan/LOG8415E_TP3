def create_standalone_group(ec2_client, sg_name, vpc_id):
    security_group = ec2_client.create_security_group(
        Description="MYSQL Standalone Security Group",
        GroupName=sg_name,
        VpcId=vpc_id
    )
    create_standalone_rules(ec2_client, security_group['GroupId'])
    return security_group

def create_cluster_group(ec2_client, sg_name, vpc_id):
    security_group = ec2_client.create_security_group(
        Description="MYSQL Cluster Security Group",
        GroupName=sg_name,
        VpcId=vpc_id
    )
    add_cluster_rules(ec2_client, security_group['GroupId'])
    return security_group

def create_proxy_group(ec2_client, sg_name, vpc_id):
    security_group = ec2_client.create_security_group(
        Description="MYSQL Proxy Security Group",
        GroupName=sg_name,
        VpcId=vpc_id
    )
    add_cluster_rules(ec2_client, security_group['GroupId'])
    return security_group

def create_standalone_rules(ec2_client, sg_id):
    inbound_rules = [
        {
            'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
        ]
    ec2_client.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=inbound_rules)
def add_cluster_rules(ec2_client, sg_id):
    inbound_rules = [
        {
            'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': '-1', 'FromPort': 1186, 'ToPort': 1186,
            'IpRanges': [{'CidrIp': '172.31.16.0/20'}]
        }
    ]
    ec2_client.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=inbound_rules)
def delete_security_group(ec2_client, sg_id):
    ec2_client.delete_security_group(GroupId=sg_id)