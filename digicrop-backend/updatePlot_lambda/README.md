# Update Plot Lambda

## Purpose
This Lambda function dynamically updates a plot's information in the DynamoDB table. It is designed to take a list of arbitrary fields in the request body and apply them to a specific plot identified by its `plotId` and `userId`.

## Node.js to Python Migration
This function was migrated directly from Node.js to Python to preserve all logic and API behaviors exactly as they were.
- Framework: Python with `boto3`
- AWS Region: `us-east-1`
- DynamoDB Table: `MainTransactionData`

## Implementation Details
- **Entry Point**: `def lambda_handler(event, context):`
- **Request Format**: JSON body containing `userId` and dynamic fields to update.
- **userId Requirement**: The `userId` is required in the JSON body as it forms the Partition Key (PK). It is excluded from the update fields.
- **plotId Handling**: The `plotId` is required and can be passed as a path parameter (priority) or a query string parameter. It forms the Sort Key (SK).
- **Dynamic Update Fields**: Any field in the request body (other than `userId`) is treated as a field to update, allowing flexible partial updates.
- **DynamoDB PK/SK Structure**: 
  - `PK` = `userId`
  - `SK` = `PD-{plotId}`
- **ConditionExpression**: `attribute_exists(PK)` ensures the item being updated already exists in DynamoDB.
- **ReturnValues**: `ALL_NEW` returns the completely updated item in the response.

## Responses
- **Successful Response**: HTTP 200 with message "Plot updated successfully" and the updated `data`.
- **Error Responses**: HTTP 400 for missing/invalid input, HTTP 500 for internal server errors.

## Example Request
**Path Parameter**: `/plot/123`
**Body**:
```json
{
  "userId": "user123",
  "cropType": "Cotton",
  "soilType": "Black Soil"
}
```

## Example Response
```json
{
  "message": "Plot updated successfully",
  "data": {
    "PK": "user123",
    "SK": "PD-123",
    "cropType": "Cotton",
    "soilType": "Black Soil"
  }
}
```
