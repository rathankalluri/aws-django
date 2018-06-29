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

def chat_json_builder(mode='', **instance):
	response = {
  "fulfillmentText": "This is a text response",
  "fulfillmentMessages": [
    {
      "card": {
        "title": "card title",
        "subtitle": "card text",
        "imageUri": "https://assistant.google.com/static/images/molecule/Molecule-Formation-stop.png",
        "buttons": [
          {
            "text": "button text",
            "postback": "https://assistant.google.com/"
          }
        ]
      }
    }
  ],
  "source": "example.com",
  "payload": {
		"slack": {
		  "text": "This is a text response for Slack."
		}
  },
  "outputContexts": [
    {
      "name": "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/context name",
      "lifespanCount": 5,
      "parameters": {
        "param": "param value"
      }
    }
  ],
  "followupEventInput": {
    "name": "event name",
    "languageCode": "en-US",
    "parameters": {
      "param": "param value"
    }
  }
}


	return None

# Combine check_status_all and check_status into one function
def check_status_all(filter):
	ec2 = boto3.resource('ec2')
	
	ec2info = defaultdict()
	
	if filter:
		filters=[{'Name': 'instance-state-name', 'Values': [filter]}]
		
	instances = ec2.instances.filter(Filters=filters)
	
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
		print(ec2info)
		pdb.set_trace()
		#json_data = chat_json_builder(ec2info)
	#return JsonResponse(json_data)	
	return JsonResponse({'message':'Still working on it'})
		
def check_status(instance_id, filter='', instance_meta=''):
	ec2 = boto3.resource('ec2')
	
	ec2info = defaultdict()
		
	if filter:
		filters=[{'Name': 'instance-state-name', 'Values': [filter]}]
	
	instances = ec2.instances.filter(InstanceIds=[instance_id],Filters=filters)
	
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
		
		print(ec2info)
		pdb.set_trace()
		#json_data = chat_json_builder(ec2info)
	#return JsonResponse(json_data)		
	return JsonResponse({'message':'Still working on it'})
	
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chat(request):
	# Add authentication by slack ID

	if request.method == "POST":
		data = json.loads(request.body)
		
		any = data['queryResult']['parameters']['any']
		instance_state = data['queryResult']['parameters']['instance_state']
		meta = data['queryResult']['parameters']['meta']
		
		STATES = ['running','stopping','stopped','shutting-down','terminated']
		META = []
		
		if any:
			instance_id = re.findall(r"(i-\w+)",any)
			instnace_id = instance_id[0]
		else:
			instance_id = False
		
		#Check individual instance, state and give required meta value
		if instance_id and (instance_state in STATES) and (meta in META):
			print("You have all the data")
		
		#Check individual instance and state it is in 
		if instance_id and (instance_state in STATES) and (meta not in META):
			print("No meta")
		
		#Check invidiual instances details
		if instance_id and (instance_state not in STATES) and (meta not in META):
			check_status(instance_id)
		
		#Checks all instancs that are on EC2
		if not instance_id and (instance_state in STATES):
			if instance_state == 'running':
				json_resp = check_status_all('running')
			if instance_state == 'stopping':
				json_resp = check_status_all('stopping')
			if instance_state == 'stopped':
				json_resp = check_status_all('stopped')
			if instance_state == 'shutting-down': 
				json_resp = check_status_all('shutting-down')
			if instance_state == 'terminated':
				json_resp = check_status_all('terminated')
			
		else:
			return JsonResponse({'Error':'Use any of these keywords (running|stopping|stopped|shutting-down|terminated)'}) #Error Message

		return JsonResponse(json_resp) #Response to bot
	return render(request, 'bot/data.html', context={'nooutput':"You landed on a wrong page please go back to Home page"},)
