import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('dinomix')

def decimal_default(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        # Convert decimal to int if it's a whole number, otherwise to float
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def get_cors_headers():
    """Return CORS headers"""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS"
    }

def lambda_handler(event, context):
    # Handle OPTIONS request for CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'message': 'CORS preflight successful'})
        }

    try:
        # Parse the POST request body
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event

        # Extract user_id and prop from the request
        user_id = body.get('user_id')
        prop_data = body.get('prop', {})

        # Validate required fields
        if not user_id:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'user_id is required'
                })
            }

        # Update the DynamoDB item
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression='SET prop = :prop_val',
            ExpressionAttributeValues={
                ':prop_val': prop_data
            },
            ReturnValues='UPDATED_NEW'
        )

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Successfully updated user data',
                'user_id': user_id,
                'updated_attributes': response.get('Attributes', {})
            }, default=decimal_default)
        }

    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Database error occurred',
                'details': str(e)
            })
        }

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return {
            'statusCode': 400,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Invalid JSON format in request body'
            })
        }

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
