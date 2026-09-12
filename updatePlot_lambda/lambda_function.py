import json
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('MainTransactionData')

def response(status_code, body):
    if isinstance(body, str):
        body = {"message": body}
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    try:
        print("Incoming event:", json.dumps(event))

        if not event.get("body"):
            return response(400, "Request body is required")

        body = json.loads(event["body"])

        path_parameters = event.get("pathParameters") or {}
        query_string_parameters = event.get("queryStringParameters") or {}

        plot_id = path_parameters.get("plotId") or query_string_parameters.get("plotId")

        if not plot_id:
            return response(400, "plotId is required")

        user_id = body.get("userId")

        if not user_id:
            return response(400, "userId is required")

        # Dynamic update fields
        update_fields = {k: v for k, v in body.items() if k != "userId"}

        if not update_fields:
            return response(400, "No fields provided for update")

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

        return response(200, {
            "message": "Plot updated successfully",
            "data": result.get("Attributes", {})
        })

    except Exception as e:
        print("Error:", e)
        return response(500, str(e))
