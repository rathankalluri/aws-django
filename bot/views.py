from django.shortcuts import render
import sys
from django.http import HttpResponse, JsonResponse
import boto3
import pdb; #Remove after debug pdb.set_trace()
from collections import defaultdict
import json
import re

# Create your views here.
def index(requests):
	return render(requests, 'bot/index.html')

def instances(requests, filter='', mode='web'):
	output = {}
	nooutput = "No running instances available"
	ec2 = boto3.resource('ec2')
	
	if filter == 'running':
		filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
	elif filter == 'stopped':
		filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
	else:
		filters=[]
		
	instances = ec2.instances.filter(Filters=filters)
	ec2rinfo = defaultdict()
	
	# Get Instance Name
	for instance in instances:
		for tag in instance.tags:
			if 'Name' in tag['Key']:
				name = tag['Value']
			else:
				name = "No Instance Name Defined"
		#Rest all info
		ec2rinfo[instance.id] = {
		'Name':name,
		'Type':instance.instance_type,
		'State':instance.state['Name'],
		'Private IP':instance.private_ip_address,
		'Public IP':instance.public_ip_address,
		'Launch Time':instance.launch_time
		}
	if mode == 'api':
		return JsonResponse(ec2rinfo)
	else:
		if ec2rinfo:
			return render(requests, 'bot/data.html', context={'output':ec2rinfo},)
		else:
			return render(requests, 'bot/data.html', context={'nooutput':nooutput},)

#CREATE instance
def create_instance(requests):
	output = {}
	nooutput = "Function not available at the moment"
	
	return render(requests, 'bot/data.html', context={'nooutput':nooutput},)

#DELETE instance
def delete_instance(requests):
	output = {}
	nooutput = "Function not available at the moment"
	
	return render(requests, 'bot/data.html', context={'nooutput':nooutput},)
	
def ec2_op(requests, op, ecid, mode='web'):
	from botocore.exceptions import ClientError
	operation = op
	instance_id = ecid
	ec2 = boto3.client('ec2')
	if operation == 'start':
		try:
			ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
		except ClientError as e:
			if 'DryRunOperation' not in str(e):
				raise
		try:
			response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
			if mode == 'api':
				return JsonResponse({'Status':'Success'})
			else:
				return render(requests, 'bot/data.html', context={'nooutput':"Instance has Started Successfully"},)
		except ClientError as e:
			if mode == 'api':
				return JsonResponse({'Error':e})
			else:
				return render(requests, 'bot/data.html', context={'nooutput':e},)
	else:
		try:
			ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
		except ClientError as e:
			if 'DryRunOperation' not in str(e):
				raise

		# Dry run succeeded, call stop_instances without dryrun
		try:
			response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
			if mode == 'api':
				return JsonResponse({'Status':'Success'})
			else:
				return render(requests, 'bot/data.html', context={'nooutput':"Instance has Stopped Successfully"},)
		except ClientError as e:
			if mode == 'api':
				return JsonResponse({'Error':e})
			else:
				return render(requests, 'bot/data.html', context={'nooutput':e},)
	# return this to all instances
	return HttpResponse("Wrong Page!!! Please go to home page")

#Chat Functions start here 

def chat_json_builder_single(ec2info):

	for id in ec2info:
		instance_id = id
	
	vals = dict(ec2info.items())
	instance_name = vals[instance_id]["instance_name"]
	instance_state = vals[instance_id]["instance_state"]
	instance_type = vals[instance_id]["instance_type"]
	instance_private_ip = vals[instance_id]["instance_private_ip"]
	instance_public_ip = vals[instance_id]["instance_public_ip"]
	
	true = 'true'
	
	if instance_state == "running":
		color_code = "good"
		button_state = "Stop Server"
		button_url = "http://127.0.0.1:8000/bot/ec2_op/stop/"+instance_id
		style = "danger"
	elif instance_state == "stopping" or instance_state == "shutting-down":
		color_code = "warning"
		button_state = "Server Stopping"
		button_url = "#"
		style = ""
	else:
		color_code = "danger"
		button_state = "Start Server"
		button_url = "http://127.0.0.1:8000/bot/ec2_op/start/"+instance_id
		style = "primary"
	
	response = {
  "fulfillmentText": "WebHook has responded with required details to Slack bot",
  "payload": {
		"slack": {
		"text": "Here are the details for "+instance_id,
		 "attachments": [
			{
            "fallback": "The server is currently "+instance_state+"",
            "text": "The server is currently "+instance_state+"",
            "fields": [
                {
                    "title": "Type",
                    "value": instance_type,
                    "short": true
                },
                {
                    "title": "Name",
                    "value": instance_name,
                    "short": true
                }
            ],
            "color": color_code,
			
			"actions": [
				{
				  "type": "button",
				  "text": button_state,
				  "url": button_url,
				  "style":style
				}
			  ]
        }
		 
		 ]
		}
  }
}
	return response

def chat_json_builder(ec2info, instance_value):
	if not instance_value:
		field_arr = []
		count = 0
		for item in ec2info.items():
			count = count+1
			instance_id = item[0]
			instance_name = item[1]["instance_name"]
			instance_state = item[1]["instance_state"]
			instance_type = item[1]["instance_type"]
			instance_private_ip = item[1]["instance_private_ip"]
			instance_public_ip = item[1]["instance_public_ip"]
			
			true = 'true'
			
			field_arr.append({
						"title": instance_id,
						"value": "The instance is "+instance_type+" and is "+instance_state
					})
		
		response = {
	  "fulfillmentText": "WebHook has responded with required details to Slack bot",
	  "payload": {
			"slack": {
			"text": "Here are the servers' details ",
			 "attachments": [
				{
				"fallback": "Here are the servers' details ",
				"fields": field_arr,
				"color": "#439FE0",
			}
			 
			 ]
			}
	  }
	}
		return response
	else:
		return chat_json_builder_single(ec2info)

def check_status(instance_id=False, filter='', instance_meta=''):
	ec2 = boto3.resource('ec2')
	json_data = ''
	ec2info = defaultdict()
	eflag = False
	
	if filter:
		filters=[{'Name': 'instance-state-name', 'Values': [filter]}]
	else:
		filters=[]
	
	if not instance_id:
		try:
			instances = ec2.instances.filter(Filters=filters)
		except ClientError as e:
			eflag = True
			msg = 'An exception occoured :'+e.response['Error']['Code']
	else:
		try:
			instances = ec2.instances.filter(InstanceIds=[instance_id],Filters=filters)
		except ClientError as e:
			eflag = True
			msg = 'An exception occoured :'+e.response['Error']['Code']
	#instances = ec2.instances.filter(InstanceIds=[instance_id],Filters=filters)
	
	for instance in instances:
		for tag in instance.tags:
			if 'Name' in tag['Key']:
				name = tag['Value']
			else:
				name = "No Instance Name Defined"
				
		ec2info[instance.id] = {
		'instance_name':name,
		'instance_type':instance.instance_type,
		'instance_state':instance.state['Name'],
		'instance_private_ip':instance.private_ip_address,
		'instance_public_ip':instance.public_ip_address
		}
		
	if eflag:
		json_data = {"fulfillmentText": msg,"payload": {"slack": {"text": msg}}}
	else:
		json_data = chat_json_builder(ec2info, instance_id)
		
	return json_data
	#return JsonResponse({'message':'Still working on it'})
	
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chat(request):
	# Add authentication by slack ID

	if request.method == "POST":
		data = json.loads(request.body)
		
		any = data['queryResult']['parameters']['any']
		instance_state = data['queryResult']['parameters']['instance_state']
		meta = data['queryResult']['parameters']['meta']
		
		source_info = data['originalDetectIntentRequest']
		print(source_info)
		user_id = data['originalDetectIntentRequest']['payload']['data']['event']['user']
		
		DATABASE = ['U0CQKNSJZ','U07AMDSR5']
		
		STATES = ['running','stopping','stopped','shutting-down','terminated']
		META = ['details']
		
		#if user_id in DATABASE: #Replace this if with a proper auth mechanism
		if any:
			instance_id = re.findall(r"(i-\w+)",any)
			if instance_id:
				instance_id = instance_id[0]
			else:
				instance_id = False

		#Check individual instance, state and give required meta value
		if instance_id and (instance_state in STATES) and (meta in META):
			return JsonResponse({"fulfillmentText": "This is a text response","payload":{"slack": {"text": "You have all the data"}}})

		#Check individual instance and state it is in 
		if instance_id and (instance_state in STATES) and (meta not in META):
			#return JsonResponse(chat_json_builder())
			return JsonResponse(check_status(instance_id=instance_id, filter=instance_state))

		#Check invidiual instances details
		if instance_id and (instance_state not in STATES) and (meta not in META):
			return JsonResponse(check_status(instance_id=instance_id))

		if not instance_id and (instance_state in STATES):
			if instance_state == 'running':
				return JsonResponse(check_status(filter='running'))
			if instance_state == 'stopping':
				return JsonResponse(check_status(filter='stopping'))
			if instance_state == 'stopped':
				return JsonResponse(check_status(filter='stopped'))
			if instance_state == 'shutting-down': 
				return JsonResponse(check_status(filter='shutting-down'))
			if instance_state == 'terminated':
				return JsonResponse(check_status(filter='terminated'))
		else:
			return JsonResponse({"fulfillmentText": "This is a text response","payload":{"slack": {"text": "Use any of these keywords (running|stopping|stopped|shutting-down|terminated)"}}}) #Error Message
		"""else:
			return JsonResponse({"fulfillmentText": "You are not authorized to work with AWS","payload":{"slack": {"text": "You are not authorized to work with AWS"}}}) #User not Authorized"""
	return render(request, 'bot/data.html', context={'nooutput':"You landed on a wrong page please go back to Home page"},)
