# TelemetryData Lambda Function

This AWS Lambda function is written in Python (compatible with Python 3.13) to retrieve telemetry data from an AWS DynamoDB table named `TelemetryData`. It acts as an equivalent replacement for a previous Node.js implementation.

## Features
- Connects to DynamoDB using `boto3`.
- Returns the latest record if only `SerialNumber` is provided.
- Returns a list of records sorted chronologically if `SerialNumber`, `startDate`, and `endDate` are provided.
- Fully JSON serializes DynamoDB `Decimal` types.
- Provides robust error handling and standardized API responses.

## Prerequisites
- Python 3.13 installed locally (if testing locally).
- AWS CLI configured with appropriate permissions.
- An existing DynamoDB table named `TelemetryData` in the `ap-south-1` region with `SerialNumber` as the Partition Key (PK) and `SK` as the Sort Key.

## Files
- `lambda_function.py`: The main AWS Lambda handler.
- `requirements.txt`: Python dependencies required for this function (only `boto3`).

## Deployment Instructions

1. **Package the Application:**
   AWS Lambda for Python already includes `boto3` in its standard runtime environment. Therefore, you do not strictly need to package `boto3` unless you require a specific newer version. For a standard deployment, you only need `lambda_function.py`.

   ```bash
   zip function.zip lambda_function.py
   ```

2. **Deploy to AWS Lambda via CLI:**
   You can update an existing Lambda function using the AWS CLI:

   ```bash
   aws lambda update-function-code \
       --function-name <YourLambdaFunctionName> \
       --zip-file fileb://function.zip \
       --region ap-south-1
   ```

   Alternatively, you can upload `lambda_function.py` directly through the AWS Lambda Management Console.

3. **Configure the Lambda Environment:**
   - **Runtime:** Set the runtime to `Python 3.13`.
   - **Handler:** Set the handler to `lambda_function.lambda_handler`.
   - **IAM Role:** Ensure the function's execution role has the `dynamodb:Query` permission on the `TelemetryData` table.

## Testing
You can test the function directly via the AWS Console or using API Gateway by passing query string parameters:
- `?SerialNumber=DEVICE123`
- `?SerialNumber=DEVICE123&startDate=2023-01-01&endDate=2023-12-31`
