import os
import json
import logging
import traceback
from datetime import datetime, UTC
import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
# We use environment variables for configuration with fallbacks
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "sentinel2-all-bands")

s3_client = boto3.client("s3", region_name=AWS_REGION)


def generate_response(status_code: int, body: dict) -> dict:
    """
    Helper function to generate API Gateway compatible JSON responses.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event: dict, context) -> dict:
    """
    Main Lambda handler for processing POST and GET requests.
    """
    try:
        logger.info(f"EVENT: {json.dumps(event, indent=2)}")

        # Determine HTTP method from event (supports different API Gateway payload formats)
        request_context = event.get("requestContext", {})
        http_context = request_context.get("http", {})
        method = http_context.get("method") or event.get("httpMethod")

        # ========================================================
        # SAVE DATA
        # ========================================================
        if method == "POST":
            body_str = event.get("body", "{}")
            if not body_str:
                body_str = "{}"
            
            body = json.loads(body_str)

            serial_number = body.get("serialNumber")
            data_type = body.get("dataType")
            result = body.get("result")

            if not serial_number or not data_type or not result:
                return generate_response(400, {
                    "success": False,
                    "message": "serialNumber, dataType and result required"
                })

            # Create S3 key: dataType_lowercase/serialNumber/serialNumber.json
            key = f"{data_type.lower()}/{serial_number}/{serial_number}.json"
            
            timestamp = datetime.now(UTC).isoformat().replace('+00:00', 'Z')

            payload = {
                "serialNumber": serial_number,
                "dataType": data_type,
                "timestamp": timestamp,
                "result": result
            }

            # Put object in S3
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=json.dumps(payload),
                ContentType="application/json"
            )

            return generate_response(200, {
                "success": True,
                "message": "Data saved to S3",
                "key": key
            })

        # ========================================================
        # FETCH DATA
        # ========================================================
        if method == "GET":
            query = event.get("queryStringParameters") or {}

            serial_number = query.get("serialNumber")
            data_type = query.get("dataType")

            if not serial_number or not data_type:
                return generate_response(400, {
                    "success": False,
                    "message": "serialNumber and dataType required"
                })

            prefix = f"{data_type.lower()}/{serial_number}/"

            # ----------------------------------------------------
            # LIST OBJECTS
            # ----------------------------------------------------
            list_response = s3_client.list_objects_v2(
                Bucket=BUCKET_NAME,
                Prefix=prefix
            )

            objects = list_response.get("Contents", [])

            if not objects:
                return generate_response(404, {
                    "success": False,
                    "message": "No data found"
                })

            # ----------------------------------------------------
            # FETCH ALL FILES
            # ----------------------------------------------------
            results = []

            for obj in objects:
                file_response = s3_client.get_object(
                    Bucket=BUCKET_NAME,
                    Key=obj["Key"]
                )
                
                body_string = file_response["Body"].read().decode("utf-8")
                results.append(json.loads(body_string))

            return generate_response(200, {
                "success": True,
                "count": len(results),
                "data": results
            })

        # ========================================================
        # METHOD NOT ALLOWED
        # ========================================================
        return generate_response(405, {
            "success": False,
            "message": "Method not allowed"
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {str(e)}")
        return generate_response(400, {
            "success": False,
            "message": "Invalid JSON in request body"
        })
    except Exception as e:
        logger.error(f"ERROR: {str(e)}\n{traceback.format_exc()}")
        return generate_response(500, {
            "success": False,
            "message": str(e),
            "stack": traceback.format_exc()
        })
