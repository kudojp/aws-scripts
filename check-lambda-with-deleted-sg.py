import sys
import boto3
import argparse
import pdb

def get_arn_to_sgs(lambda_client):
	function_arn_to_sg = {}

	# Pagination loop
	paginator = lambda_client.get_paginator('list_functions')
	response_iterator = paginator.paginate()

	for response in response_iterator:
		for function in response['Functions']:
			if 'VpcConfig' not in function:
				print(function['FunctionArn'], "(without VpcConfig)")
				continue
			# function_name = function['FunctionName']
			function_arn = function['FunctionArn']
			function_arn_to_sg[function_arn] = function['VpcConfig']['SecurityGroupIds']
	return function_arn_to_sg

def check_sg_existence(ec2_client, sg_id):
	try:
		ec2_client.describe_security_groups(GroupIds=[sg_id])
	except Exception as e:
		print("@@@ ", e)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog="Default security groups detecter",
		description="This lists the resources which uses 'default' security groups",
	)
	parser.add_argument('-p', '--profile', required=True)
	args = parser.parse_args()

	my_session = boto3.Session(profile_name=args.profile)
	sts_client = my_session.client('sts')
	account_id = sts_client.get_caller_identity()['Account']

	print('Account is: ' + account_id)
	agree = input('Is it OK? (y/n): ')
	if agree != 'y': sys.exit()

	ec2_client = my_session.client('ec2')
	regions = ec2_client.describe_regions()['Regions']

	for region in regions:
		region_name = region['RegionName']
		print()
		print('\n' + region_name, '-' * 30, '\n')
		lambda_client = my_session.client('lambda', region_name = region_name)
		ec2_client = my_session.client('ec2', region_name = region_name)

		function_arn_to_sgs = get_arn_to_sgs(lambda_client)
		for function_arn, sgs in function_arn_to_sgs.items():
			print(function_arn)
			for sg in sgs:
				check_sg_existence(ec2_client, sg)
