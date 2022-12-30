import json
import boto3

def upload_items():
    with open('student_data.json', 'r') as datafile:
        records = json.load(datafile)

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    student_table = dynamodb.Table('paas-2-student')

    for record in records:
        student_table.put_item(Item=record)

def get_item():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    student_table = dynamodb.Table('paas-2-student')
    item = student_table.get_item(Key={'name': 'mr_bean'})['Item']
    print(item)
    print(f"{item['name']},{item['major']},{item['year']}")

upload_items()
get_item()
