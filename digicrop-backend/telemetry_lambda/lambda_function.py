import json
import logging
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the DynamoDB resource
# Using region "ap-south-1" as requested
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('TelemetryData')

class DecimalEncoder(json.JSONEncoder):
    """
    Helper class to convert Decimal types to float/int for JSON serialization.
    DynamoDB returns numeric values as Decimals.
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert to int if there's no fractional part, otherwise float
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def generate_response(status_code, body):
    """
    Helper function to generate consistent API Gateway response.
    Includes CORS headers and Content-Type.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }

def lambda_handler(event, context):
    """
    Main Lambda handler to process incoming API Gateway requests.
    """
    try:
        # Extract query string parameters safely
        query_params = event.get('queryStringParameters') or {}
        serial_number = query_params.get('SerialNumber')
        start_date = query_params.get('startDate')
        end_date = query_params.get('endDate')

        # SerialNumber is a required parameter
        if not serial_number:
            logger.warning("Missing SerialNumber in request")
            return generate_response(400, {"message": "Missing SerialNumber"})

        # Logic based on presence of startDate and endDate
        if not start_date or not end_date:
            # Only SerialNumber is provided: return the latest record
            logger.info(f"Querying latest record for SerialNumber: {serial_number}")
            response = table.query(
                KeyConditionExpression=Key('SerialNumber').eq(serial_number),
                ScanIndexForward=False, # Sort descending to get the latest
                Limit=1
            )
        else:
            # Both start and end dates are provided: return records in the range
            logger.info(f"Querying records for SerialNumber: {serial_number} between {start_date} and {end_date}")
            response = table.query(
                KeyConditionExpression=Key('SerialNumber').eq(serial_number) & Key('SK').between(start_date, end_date),
                ScanIndexForward=True # Sort ascending
            )

        items = response.get('Items', [])

        # Handle no data found
        if not items:
            logger.info("No data found for the given parameters")
            return generate_response(404, {"message": "No data found"})

        # If it was a single record query, return the first item as an object, else the list
        if not start_date or not end_date:
            result_data = items[0]
        else:
            result_data = items

        return generate_response(200, result_data)

    except Exception as e:
        # Catch all other exceptions to prevent Lambda crashes and return standard 500 error
        logger.error(f"Server error: {str(e)}", exc_info=True)
        return generate_response(500, {
            "message": "Server error",
            "error": str(e)
        })
