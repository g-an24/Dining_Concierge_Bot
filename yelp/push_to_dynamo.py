import boto3
import json
from decimal import Decimal
from botocore.exceptions import ClientError

# Initialize a Boto3 DynamoDB resource
dynamodb = boto3.resource('dynamodb',aws_access_key_id='ACCESS_KEY', aws_secret_access_key='SECRET_KEY', region_name='region')

# Specify your DynamoDB table name
table_name = 'yelp-restaurants'
table = dynamodb.Table(table_name)

def load_data_to_dynamodb(filename):
    # Open and read the JSON file
    with open(filename) as file:
        items = json.load(file)
        
    # Iterate over items and put each into the DynamoDB table
    for item in items:
        print(f"Adding item: {item['business_id']['S']}")
        # Convert float values to Decimal
        item['rating']['N'] = Decimal(str(item['rating']['N']))
        item['number_of_reviews']['N'] = Decimal(str(item['number_of_reviews']['N']))
        
        response = table.put_item(Item={
            'business_id': item['business_id']['S'],
            'insertedAtTimestamp': item['insertedAtTimestamp']['S'],
            'name': item['name']['S'],
            'address': item['address']['S'],
            'coordinates': item['coordinates']['S'],
            'number_of_reviews': item['number_of_reviews']['N'],  # Already converted to Decimal
            'rating': item['rating']['N'],  # Already converted to Decimal
            'zip_code': item['zip_code']['S'],
            'cuisine': item['cuisine']['S'],
        })
        print(f"Item added: {item['business_id']['S']}")

# Replace 'yelp_data_dynamodb.json' with the path to your JSON file
load_data_to_dynamodb('Data path from local machine')