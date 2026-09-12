# Update Plot Lambda

This Lambda function updates a plot's transaction data dynamically in DynamoDB. It was migrated from Node.js to Python using `boto3`.

## AWS Configuration
- **Lambda Name:** Update Plot
- **Region:** `us-east-1`
- **DynamoDB Table:** `MainTransactionData`

## Implementation Details
- **Entry point:** `lambda_function.lambda_handler`
- **PK/SK Structure:** 
  - `PK` = `userId` (Partition Key)
  - `SK` = `PD-{plotId}` (Sort Key)
- The table requires that the item exists before the update, utilizing `ConditionExpression: "attribute_exists(PK)"`.
- The update operation dynamically maps all provided fields in the request payload except `userId` into a DynamoDB `UpdateExpression`.
- Returns the complete updated item via `ReturnValues="ALL_NEW"`.

## Request Format

- `plotId` is fetched from either `pathParameters` or `queryStringParameters` (Path parameter takes priority).
- `userId` is required in the JSON request body.
- Any additional fields provided in the JSON request body are dynamically mapped to update fields.

### Example Request

**Path/Query Parameter:** `plotId=789`

**Request Body:**
```json
{
    "userId": "user123",
    "cropType": "Cotton",
    "soilType": "Black Soil",
    "variety": "BT Cotton"
}
```

### Example Response (Success 200)

```json
{
    "message": "Plot updated successfully",
    "data": {
        "PK": "user123",
        "SK": "PD-789",
        "cropType": "Cotton",
        "soilType": "Black Soil",
        "variety": "BT Cotton",
        "...": "..."
    }
}
```

### Example Error Responses (400)

- If `plotId` is missing: `{"message": "plotId is required"}`
- If `userId` is missing: `{"message": "userId is required"}`
- If no update fields are provided: `{"message": "No fields provided for update"}`
