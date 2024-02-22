

import boto3
import json
import random
import requests

sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
es_client = boto3.client('es')

def lambda_handler(event, context):

    ses_client = boto3.client('ses')

    queue_url = 'SQS Queue URL'
    ids = []
    sqs_response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All']
    )

    if 'Messages' in sqs_response:
        message = sqs_response["Messages"][0]
        receipt_handle = message['ReceiptHandle']

        if 'MessageAttributes' in message:
            message_attributes = message['MessageAttributes']
            cuisine_type = message_attributes['Cuisine']['StringValue'] if 'Cuisine' in message_attributes else None
            location = message_attributes['Location']['StringValue'] if 'Location' in message_attributes else None
            email = message_attributes['email']['StringValue'] if 'email' in message_attributes else None
            num_people = message_attributes['NumberOfPeople'][
                'StringValue'] if 'NumberOfPeople' in message_attributes else None
            date = message_attributes['DiningDate']['StringValue'] if 'DiningDate' in message_attributes else None
            time = message_attributes['DiningTime']['StringValue'] if 'DiningTime' in message_attributes else None

            user_details = {
                'Location': 'Manhattan',
                'Cuisine': cuisine_type,
                'Number_people': num_people,
                'Date': date,
                'Time': time
            }
        print(cuisine_type, "===============")
        es_response = es_query_for_cuisine(es_client, cuisine_type)
        print("====================================== ES ========================",es_response)
        print("Received message attributes:", message_attributes)


        if len(es_response) > 0:
            ids = random.sample(es_response, 3)
        
        restaurants = []
        
        for id in ids:    
            restaurant_info = fetch_restaurant_info(dynamodb, id)
            restaurants.append(restaurant_info)

        
        
        email_body = format_email_body(restaurants, user_details)
        
        resp = save_user_search(email, location, cuisine_type, email_body)
        
        if resp:
            print("Previous recommendations for {email} loaded successfully.")

        send_email(ses_client, 'Receivers Email', email_body)
        
        
        print(f"Location before save_user_search: {location}")
        #new line added ====================================================================
        
        
        

        
        sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

        message = {
            'message': 'Email sent succesfully'
        }

        return {

            'statusCode': 200,
            'body': json.dumps(message)
        }

    else:
        return {
            'statusCode': 200,
            'body': json.dumps('No message in queue')
        }

# new function added ====================================================================================

def save_user_search(email, location, cuisine, restaurants):
    print(f"Inside save_user_search, location: {location}")
    try:
        table_name = 'previous-recs'
        table = dynamodb.Table(table_name)
        
        
        
        response = table.put_item(
            Item = {
                'email': email,
                'location': 'Manhattan',
                'cuisine': cuisine,
                'restaurants':restaurants
            }
        )
        
        return True;
        
    except Exception as e:
        print(e)
        return False


def es_query_for_cuisine(es_client, cuisine_type):
    es_url = 'Open Search URL'
    headers = {'Content-Type': 'application/json'}
    auth = ('Username', 'Password')
    query = {
        "query": {
            "match": {
                "cuisine": cuisine_type
            }
        },  "size":100
    }
    try:
        response = requests.get(es_url, headers=headers, auth=auth, data=json.dumps(query))
        if response.status_code == 200:
            results = response.json()
            print(results['hits']['hits'][0]['_source']['business_id'])
            
            ids = []
            for res in results['hits']['hits']:
                id = res['_source']['business_id']
                ids.append(id)
            return ids
        
    except Exception as e:
        print(e)
    return [] # if error comes put this return [] on line 135==================================

def fetch_restaurant_info(dynamodb, restaurant_id):
    table_name = 'yelp-restaurants'
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(
            Key={'business_id': restaurant_id}
        )

        if 'Item' in response:

            return response['Item']
        else:
            print(f"No item found with id: {restaurant_id}")
            return None
    except Exception as e:
        print(f"Failed to fetch item from DynamoDB: {str(e)}")
        return None


def format_email_body(restaurants_info, user_details):
    html = """<tr style="background-color: #f2f2f2;">
    <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Name</th>
    <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Rating</th>
    <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Review Count</th>
    <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Address</th>
    """

    for data in restaurants_info:
        address = data['address'].replace("\'", '').replace('[', '').replace(']', '').replace('"', '')

        # Append a row to the table for each JSON object
        html += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{data['name']}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{data['rating']}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{data['number_of_reviews']}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{address}</td>
                </tr>
        """

    html_1 = f'''<html><head></head><body><p>Here are the requested suggestions for the following details: <br> Location: {user_details['Location']} <br> 
    Number of people: {user_details['Number_people']} <br>
    Cuisine: {user_details['Cuisine']} <br>
    Date: {user_details['Date']} <br>
    Time: {user_details['Time']} <br>
    </p><p><table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">>'''
    html_2 = "</table></p></body></html>"

    print(html_1 + html + html_2)

    return html_1 + html + html_2


def send_email(ses_client, email, email_body):
    sender_email = "Senders email"

    subject = "Restaurant Recommendations"

    try:
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [
                    email
                ]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': 'Here are your recommendations!',
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': email_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print("Email sent! Message ID:", response['MessageId'])
    except Exception as e:
        print(f"Failed to send email: {str(e)}")