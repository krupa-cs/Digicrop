# Sentinel-2 S3 Data Manager (Python Lambda)

## Project Overview
This project contains an AWS Lambda function migrated from Node.js to Python 3.13. It serves as an API backend to save and fetch Sentinel-2 data to/from an Amazon S3 bucket.

## Folder Structure
```text
sentinel2_python_lambda/
├── lambda_function.py  # Main Lambda handler code
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
├── test_lambda.py      # Local unit tests
└── openapi.yaml        # OpenAPI/Swagger API specification
```

## Deployment Steps
1. Package the Lambda function along with `boto3` (if a newer version is needed than the one provided by the Lambda runtime).
   ```bash
   pip install -r requirements.txt -t .
   zip -r function.zip .
   ```
2. Create/Update the AWS Lambda function using Python 3.13 runtime.
3. Upload `function.zip` to the Lambda function.
4. Configure the following Environment Variables in the AWS Console:
   - `AWS_REGION` (default: ap-south-1)
   - `BUCKET_NAME` (default: sentinel2-all-bands)
5. Connect your API Gateway to the Lambda function (proxy integration).

## Required IAM Permissions
The Lambda execution role must have the following permissions to interact with S3 and CloudWatch (for logging):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::sentinel2-all-bands",
                "arn:aws:s3:::sentinel2-all-bands/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

## API Documentation

### 1. Save Data (POST /data)
Saves Sentinel-2 data into the S3 bucket.

**Request Body:**
```json
{
  "serialNumber": "S180H120L126-02-1220:47:59",
  "dataType": "SENTINEL2",
  "result": {
     "band1": 0.45,
     "band2": 0.67
  }
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Data saved to S3",
  "key": "sentinel2/S180H120L126-02-1220:47:59/S180H120L126-02-1220:47:59.json"
}
```

### 2. Fetch Data (GET /data)
Fetches all Sentinel-2 JSON objects for a specific serial number and data type.

**Query Parameters:**
- `serialNumber` (string) - Required
- `dataType` (string) - Required

**Example Request:**
`GET /data?serialNumber=S180H120L126-02-1220:47:59&dataType=SENTINEL2`

**Success Response (200 OK):**
```json
{
  "success": true,
  "count": 1,
  "data": [
    {
      "serialNumber": "S180H120L126-02-1220:47:59",
      "dataType": "SENTINEL2",
      "timestamp": "2026-08-01T10:30:00.000Z",
      "result": {
         "band1": 0.45,
         "band2": 0.67
      }
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields.
- `404 Not Found`: No data found for the given criteria.
- `405 Method Not Allowed`: Invalid HTTP method.
- `500 Internal Server Error`: Server-side errors.
