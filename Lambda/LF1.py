import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
import json
import re
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
dynamodb_resource = boto3.resource('dynamodb')
ses_client = boto3.client('ses')



# Make sure to define your SQS_URL at the top of your Lambda function, or fetch it from environment variables or another configuration.

SQS_URL = "SQS Queue URL"

def sendSQS(request_data):
    # Instantiate SQS client using Lambda execution role permissions
    sqs_client = boto3.client('sqs')

    # Assuming request_data keys are exactly as they appear here and match the case used in your slots
    location = request_data["Location"]
    cuisine = request_data["Cuisine"]
    number_of_people = request_data["NumberOfPeople"]
    dining_date = request_data["DiningDate"]
    dining_time = request_data["DiningTime"]
    email = request_data["email"]

    # Message attributes setup
    message_attributes = {
        "location": {
            'DataType': 'String',
            'StringValue': location
        },
        "Cuisine": {
            'DataType': 'String',
            'StringValue': cuisine
        },
        "NumberOfPeople": {
            'DataType': 'Number',
            'StringValue': number_of_people
        },
        "DiningDate": {
            'DataType': 'String',
            'StringValue': dining_date
        },
        "DiningTime": {
            'DataType': 'String',
            'StringValue': dining_time
        },
        "email": {
            'DataType': 'String',
            'StringValue': email
        }
    }

    # The body of the message
    body = 'Restaurant slots'

    # Sending the message to the SQS queue
    response = sqs_client.send_message(
        QueueUrl=SQS_URL,  
        MessageAttributes=message_attributes, 
        MessageBody=body
    )

    return response 
""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """




def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    return response

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def valid_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True
    return False



def validate_dining_suggestions(location, cuisine, number_of_people, dining_date, dining_time, email):

    # Locations
    locations = ['manhattan']
    cuisines = ['chinese', 'indian', 'italian', 'japanese', 'korean', 'mex']
    if location is not None and location.lower() not in locations:
        return build_validation_result(False,
                                       'Location',
                                       'We do not have dining suggestions for {}, would you like suggestions for other locations?  '
                                       'Our most popular location is Manhattan'.format(location))

    # Cuisine
    if cuisine is not None and cuisine.lower() not in cuisines:
        return build_validation_result(False, 'Cuisine',
                                       'We do not have suggestions for {}, would you like suggestions for another cuisine?'
                                       'Our most popular cuisine is Italian'.format(cuisine))

    # Number of people
    if number_of_people is not None:
        number_of_people = parse_int(number_of_people)
        if not 0 < number_of_people < 30:
            return build_validation_result(False, 'NumberOfPeople', '{} does not look like a valid number, '
                                           'please enter a number less than 30'.format(number_of_people))

    # DiningDate
    if dining_date is not None:
        if not isvalid_date(dining_date):
            return build_validation_result(False, 'DiningDate', 'I did not understand that, what date would you like for your suggestion?')
        elif datetime.datetime.strptime(dining_date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'DiningDate', 'You can pick a date from today onwards.  What day would you like for your suggestion?')

    # DiningTime
    if dining_time is not None:
        if len(dining_time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DiningTime', None)

        hour, minute = dining_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DiningTime', None)

        # Edge case
        ctime = datetime.datetime.now()

        if datetime.datetime.strptime(dining_date, "%Y-%m-%d").date() == datetime.datetime.today():
            if (ctime.hour >= hour and ctime.minute > minute) or ctime.hour < hour or (ctime.hour == hour and minute <= ctime.minute):
                return build_validation_result(False, 'DiningTime', 'Please select a time in the future.')

    # email
    if email is not None:
        if not valid_email(email):
            return build_validation_result(False, 'email', '{} is not a valid email,'
                                           'please enter a valid email'.format(email))

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """
def dining_suggestions(intent_request):
    slots = get_slots(intent_request)
    location = slots["Location"]  # Note: This is lowercase, as per your code snippet
    cuisine = slots["Cuisine"]
    number_of_people = slots["NumberOfPeople"]
    dining_date = slots["DiningDate"]
    dining_time = slots["DiningTime"]
    email = slots["email"]
    source = intent_request['invocationSource']
    
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # request_data = {
    #     "Location": location,
    #     "Cuisine": cuisine,
    #     "NumberOfPeople": number_of_people,
    #     "DiningDate": dining_date,
    #     "DiningTime": dining_time,
    #     "email": email
    # }

    # output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    # output_session_attributes['requestData'] = json.dumps(request_data)
    
    
    if email:
        last_searched_content = checkPreviousSearches(email)  # Assuming dynamodb_client is defined globally
        if last_searched_content:
            # Logic to send an email with previous suggestions
            send_restaurant_suggestions_email(last_searched_content)
            #print(f"SES send_email response: {response}")
            
            # Construct the response content
            next_slot_to_elicit = "Location"
            response_content = f"Hi! Your previously suggested recommendations were emailed to you. How else can I assist you today?"
            # Respond to Lex with the previous suggestions
            return elicit_slot(output_session_attributes, intent_request['currentIntent']['name'], slots, next_slot_to_elicit, {'contentType': 'PlainText', 'content': response_content})
        else:
            # Update the session attributes with the request data
            request_data = {
                "Location": location,
                "Cuisine": cuisine,
                "NumberOfPeople": number_of_people,
                "DiningDate": dining_date,
                "DiningTime": dining_time,
                "email": email
            }
            output_session_attributes['requestData'] = json.dumps(request_data)

    if source == 'DialogCodeHook':
        validation_result = validate_dining_suggestions(location, cuisine, number_of_people, dining_date, dining_time, email)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'], intent_request['currentIntent']['name'], slots, validation_result['violatedSlot'], validation_result['message'])
        
        return delegate(output_session_attributes, slots)
    sendSQS(request_data)

    return close(intent_request['sessionAttributes'], 'Fulfilled', {'contentType': 'PlainText', 'content': 'You’re all set. Expect my suggestions shortly! Have a good day.'})
    
""" --- Intents --- """

def greeting_intent(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Hi there, how can I help?'})

def thank_you_intent(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': "You're welcome."})

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return dining_suggestions(intent_request)
    elif intent_name == 'GreetingIntent':
        return greeting_intent(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank_you_intent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


def checkPreviousSearches(email):
    # Reference the 'previous-records' table
    table = dynamodb_resource.Table('previous-recs')
    print(f"Checking previous searches for email: {email}")
    
    try:
        # Query the table using the primary partition key 'email'
        response = table.get_item(
            Key={
                'email': email  # This matches the partition key of your table
            }
        )
        print(f"DynamoDB response: {response}")
        
        if 'Item' in response:
            # Assuming 'restaurants' is the attribute you want from the item
            # The response['Item'] is a dictionary of the record fetched from the table
            return response['Item']
        else:
            print("No previous restaurant suggestions found for this email.")
            return None
    except Exception as e:
        print(f"Error fetching previous restaurant suggestions from DynamoDB: {e}")
        return None
        
""" --- Send Email  --- """
def send_restaurant_suggestions_email(item):
    # Extract the HTML string containing the restaurant suggestions
    restaurants_html = item['restaurants']
    
    # Now, use this HTML string as the body of your email
    try:
        response = ses_client.send_email(
            Source='Senders email',
            Destination={'ToAddresses': [item['email']]},
            Message={
                'Subject': {'Data': 'Your Previous Restaurant Suggestions'},
                'Body': {
                    'Html': {'Data': restaurants_html}  # Send the HTML content in the email
                }
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"An error occurred: {e.response['Error']['Message']}")

""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    return dispatch(event)