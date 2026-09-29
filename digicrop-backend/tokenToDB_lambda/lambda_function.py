import uuid
import logging
import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table_name = "MainTransactionData"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    user_id = event.get("userID")
    token_id = event.get("tokenId")
    column_name_to_update = "Token"

    try:
        response = table.query(
            KeyConditionExpression=Key('PK').eq(user_id) & Key('SK').begins_with('ExpoToken')
        )
        items = response.get('Items', [])
        logger.info(f"existing {items}")

        if items and len(items) > 0:
            existing_sk = items[0]['SK']
            update_response = table.update_item(
                Key={
                    'PK': user_id,
                    'SK': existing_sk
                },
                UpdateExpression="SET #columnName=:newValue",
                ExpressionAttributeNames={
                    "#columnName": column_name_to_update
                },
                ExpressionAttributeValues={
                    ":newValue": token_id
                },
                ReturnValues="ALL_NEW"
            )
            return {
                "statusCode": 200,
                "body": update_response.get('Attributes', {})
            }
        else:
            new_uuid = str(uuid.uuid4())
            new_item = {
                "PK": user_id,
                "SK": f"ExpoToken-{new_uuid}",
                "Token": token_id
            }
            table.put_item(Item=new_item)
            return {
                "statusCode": 200,
                "body": "Successfully created Item"
            }
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": "Error updating or creating item"
        }
