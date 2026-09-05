# updateSoilData_lambda

## Purpose
This AWS Lambda function updates soil-related information for an existing plot. It was migrated from Node.js to Python.

## AWS Resources
- **Region**: us-east-1
- **DynamoDB Table**: MainTransactionData

## DynamoDB Key Structure
- **PK**: `userId` (e.g., `USER123`)
- **SK**: `PD-{plotId}` (e.g., `PD-abc456`)

## Fields Updated
- `soil_ph`
- `e_c`
- `organic_carbon`
- `soil_test`
- `updatedAt` (ISO 8601 timestamp)

## HTTP/API Behavior
The Lambda expects an API Gateway event with a JSON body (or pre-parsed dict).

### Request Body
```json
{
    "userId": "...",
    "plotId": "...",
    "soil_ph": 6.5,
    "e_c": 1.2,
    "organic_carbon": 2.5,
    "soil_test": true
}
```

### Successful Response (HTTP 200)
```json
{
    "success": true,
    "data": {
        "PK": "...",
        "SK": "...",
        "soil_ph": 6.5,
        "e_c": 1.2,
        "organic_carbon": 2.5,
        "soil_test": true,
        "updatedAt": "2026-09-05T10:00:00.000Z"
    }
}
```

### Error Response (HTTP 500)
```json
{
    "success": false,
    "error": "Error message details"
}
```

## How the Python Lambda works
1. Reads `event.body` (parsing if it's a JSON string).
2. Extracts required fields (`userId`, `plotId`, `soil_ph`, etc.). Missing fields are assigned `None` (which boto3 translates to null in DynamoDB).
3. Connects to `MainTransactionData` via `boto3`.
4. Performs an `update_item` operation using `PK` and `SK`.
5. Updates the provided fields and sets `updatedAt` to the current UTC ISO timestamp.
6. Returns `ReturnValues="ALL_NEW"` which includes the fully updated attributes in the response.
