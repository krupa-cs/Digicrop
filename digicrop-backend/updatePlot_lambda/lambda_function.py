import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = "MainTransactionData"
table = dynamodb.Table(table_name)

def build_response(status_code, body):
    response_body = body
    if isinstance(body, str):
        response_body = {"message": body}
        
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(response_body)
    }

def lambda_handler(event, context):
    try:
        logger.info(f"Incoming event: {json.dumps(event)}")

        if not event.get("body"):
            return build_response(400, "Request body is required")

        body = json.loads(event["body"])

        path_params = event.get("pathParameters") or {}
        query_params = event.get("queryStringParameters") or {}

        plot_id = path_params.get("plotId") or query_params.get("plotId")

        if not plot_id:
            return build_response(400, "plotId is required")

        user_id = body.get("userId")

        if not user_id:
            return build_response(400, "userId is required")
            
        update_fields = {k: v for k, v in body.items() if k != "userId"}

        if not update_fields:
            return build_response(400, "No fields provided for update")

        update_expression_parts = []
        expression_attribute_names = {}
        expression_attribute_values = {}

        for key, value in update_fields.items():
            update_expression_parts.append(f"#{key} = :{key}")
            expression_attribute_names[f"#{key}"] = key
            expression_attribute_values[f":{key}"] = value

        update_expression = "SET " + ", ".join(update_expression_parts)

        result = table.update_item(
            Key={
                "PK": user_id,
                "SK": f"PD-{plot_id}"
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ConditionExpression="attribute_exists(PK)",
            ReturnValues="ALL_NEW"
        )

        return build_response(200, {
            "message": "Plot updated successfully",
            "data": result.get("Attributes", {})
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return build_response(500, str(e))
