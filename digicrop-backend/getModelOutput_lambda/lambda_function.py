import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Custom JSON encoder to safely handle DynamoDB Decimal values
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 > 0:
                return float(obj)
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table("CGIModelResults")

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
}

def lambda_handler(event, context):
    try:
        method = event.get("httpMethod")
        if not method and "requestContext" in event:
            method = event.get("requestContext", {}).get("http", {}).get("method")

        if method == "POST":
            raw_body = event.get("body")
            if isinstance(raw_body, str):
                body = json.loads(raw_body)
            elif isinstance(raw_body, dict):
                body = raw_body
            else:
                body = {}

            user_id = body.get("userId")
            serial_number = body.get("serialNumber")
            data_type = body.get("dataType")
            timestamp = body.get("timestamp")
            payload = body.get("payload")

            if not user_id or not serial_number or not data_type or not timestamp or payload is None:
                return {
                    "statusCode": 400,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({
                        "success": False,
                        "message": "Missing required fields"
                    })
                }

            normalized_data_type = data_type.upper()
            created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            item = {
                "PK": user_id,
                "SK": f"{timestamp}#{serial_number}#{normalized_data_type}",
                "serialNumber": serial_number,
                "dataType": normalized_data_type,
                "timestamp": timestamp,
                "payload": payload,
                "createdAt": created_at
            }

            table.put_item(Item=item)

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "success": True,
                    "message": "Data saved successfully",
                    "item": item
                }, cls=DecimalEncoder)
            }

        elif method == "GET":
            query = event.get("queryStringParameters") or {}
            user_id = query.get("userId")
            serial_number = query.get("serialNumber")
            data_type = query.get("dataType")
            date = query.get("date")

            # Mode A: serialNumber and dataType are both supplied (takes precedence)
            if serial_number and data_type:
                params = {
                    "TableName": "CGIModelResults",
                    "IndexName": "GSI_SN",
                    "KeyConditionExpression": "serialNumber = :sn AND dataType = :dt",
                    "ExpressionAttributeValues": {
                        ":sn": serial_number,
                        ":dt": data_type.upper()
                    },
                    "ScanIndexForward": False
                }
                result = table.query(**params)
                items = result.get("Items", [])

                if date:
                    items = [item for item in items if (item.get("timestamp") or "").startswith(date)]

                return {
                    "statusCode": 200,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({
                        "success": True,
                        "count": len(items),
                        "data": items
                    }, cls=DecimalEncoder)
                }

            # Mode B: userId is supplied
            if not user_id:
                return {
                    "statusCode": 400,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({
                        "success": False,
                        "message": "Either userId OR serialNumber+dataType required"
                    })
                }

            if date:
                params = {
                    "TableName": "CGIModelResults",
                    "KeyConditionExpression": "PK = :pk AND begins_with(SK, :date)",
                    "ExpressionAttributeValues": {
                        ":pk": user_id,
                        ":date": date
                    },
                    "ScanIndexForward": False
                }
            else:
                params = {
                    "TableName": "CGIModelResults",
                    "KeyConditionExpression": "PK = :pk",
                    "ExpressionAttributeValues": {
                        ":pk": user_id
                    },
                    "ScanIndexForward": False
                }

            result = table.query(**params)
            items = result.get("Items", [])

            if data_type:
                normalized_dt = data_type.upper()
                items = [item for item in items if item.get("dataType") == normalized_dt]

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "success": True,
                    "count": len(items),
                    "data": items
                }, cls=DecimalEncoder)
            }

        else:
            return {
                "statusCode": 405,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "success": False,
                    "message": "Method not allowed"
                })
            }

    except Exception as error:
        logger.error("ERROR: %s", str(error), exc_info=True)
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "success": False,
                "message": "Internal server error",
                "error": str(error)
            })
        }
