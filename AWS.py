'''
Purpose - Python script to stop/start AWS EC2 instances using Tag values
Developer - K.Janarthanan
Date - 23/1/2020
'''

import boto3
from botocore.exceptions import ClientError
import sys

aws_access_key_id = "xxxxx"
aws_secret_access_key = "xxxxx"

#Input AWS Region, Stop/Start/ Tag values
aws_region=input("\nAWS Region : ")
tag_key=input("Tag Key : ")
tag_value=input("Tag Value : ")

while (True):
    functionality=input("Press '1' to Start or '2' to Stop EC2 : ")
    if (functionality=='1' or functionality=='2'):
        break

try:
    ec2client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,region_name=aws_region)
except:
    print("Error, please check whether service name is correct")
    sys.exit(1)

#To count no of EC2 instances in the region
total_ec2=0

try:
    i=len(ec2client.describe_instances()['Reservations'])
except:
    print("Check credentials / region name are correct ")
    sys.exit(1)

#This is used because if multiple instances are launched at once, then they will be under the same Revervation->Instances []
for a in range(i):
    total_ec2+=len((ec2client.describe_instances()['Reservations'][a]['Instances']))

print("\nTotal No.of EC2 instances in the region "+aws_region+" : "+str(total_ec2))

response = ec2client.describe_instances(Filters=[{'Name': 'tag:'+tag_key,'Values': [tag_value]}])

#Extracting each instances into list
instancelist = []
for reservation in (response["Reservations"]):
    for instance in reservation["Instances"]:
         
        instancelist.append(instance)

print("\nTotal No.of EC2 instances in the region "+aws_region+" with matching Tags: "+str(len(instancelist)))

#Shutdown EC2 and Store data in JSON
json_data=[]
for each_ec2 in instancelist:

    mydict={}
    add_data=0

    if (functionality=='1'):
        if(each_ec2['State']['Name']=='stopped'): #Power on instances which are stopped. Ignore already running instances
            try:
                response = ec2client.start_instances(InstanceIds=[each_ec2["InstanceId"]] , DryRun=False)
                add_data=1
            except:
                print("Something went wrong while powering on EC2 : "+each_ec2["InstanceId"])
    else:
        if(each_ec2['State']['Name']=='running'): #Stop instances which are running. Ignore already stopped instances
            try:
                response = ec2client.stop_instances(InstanceIds=[each_ec2["InstanceId"]] , DryRun=False)
                add_data=1
            except:
                print("Something went wrong while stopping EC2 : "+each_ec2["InstanceId"])
    
    #Output only when change is made
    if(add_data==1):
        mydict['instance_id']=each_ec2["InstanceId"]
        mydict['private_ip_address']=each_ec2["PrivateIpAddress"]
        mydict['image_id']=each_ec2["ImageId"]
        json_data.append(mydict)


#Print Output 
print("\n\nOutput->\n"+str(json_data))