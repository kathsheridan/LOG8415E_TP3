def create_standalone_group(ec2_client, sg_name, vpc_id):
    security_group = ec2_client.create_security_group(
        Description="MYSQL Standalone Security Group",
        GroupName=sg_name,
        VpcId=vpc_id
    )
    create_standalone_rules(ec2_client, security_group['GroupId'])
    return security_group

def create_standalone_rules(ec2_client, sg_id):

    inbound_rules = [
        {
            'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
        ]
    ec2_client.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=inbound_rules)

def delete_security_group(ec2_client, sg_id):
    ec2_client.delete_security_group(GroupId=sg_id)