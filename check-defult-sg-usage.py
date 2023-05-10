# Mostly copied from: https://dev.classmethod.jp/articles/listup_default_security_group/ 

import sys
import boto3

my_session = boto3.Session(profile_name='ad:dev-backend')
sts_client = my_session.client('sts') # Clientオブジェクト生成
account_id = sts_client.get_caller_identity()['Account']

print('Account is: ' + account_id)
agree = input('Is it OK? (y/n): ')
if agree != 'y': sys.exit()

ec2_client = my_session.client('ec2')
regions = ec2_client.describe_regions()['Regions']

try:
	for region in regions:
		region_name = region['RegionName']
		print("# " + region_name)
		# get default security group list
		ec2 = my_session.resource('ec2', region_name=region_name)
		sgs = list(ec2.security_groups.filter(Filters=[{'Name': 'group-name', 'Values': ['default']}]))
		print('  DefaultSecurityGroups:')
		# get sg relations
		config = my_session.client('config', region_name=region_name)
		for sg in sgs:
			r = config.get_resource_config_history(
				resourceType='AWS::EC2::SecurityGroup',
				resourceId=sg.id
			)
			print("    SG: %s, VPC: %s." % (sg.id, sg.vpc_id))
			for relation in r["configurationItems"][0]["relationships"]:
				print("      " + relation["relationshipName"] + ": " + relation["resourceId"])
except Exception as e:
	print(e)
