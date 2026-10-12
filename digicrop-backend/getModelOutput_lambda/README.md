# getModelOutput Lambda Function (Python)

## Overview
The `getModelOutput` AWS Lambda function handles storing and retrieving crop/model analysis results (such as NDVI, sensor, or weather predictions) in Amazon DynamoDB.

> **Note**: This Lambda function is a direct Python migration of the original Node.js implementation (`@aws-sdk/client-dynamodb` / `@aws-sdk/lib-dynamodb`) using Python 3 and `boto3`.

---

## Configuration & Environment
- **Runtime**: Python 3.x
- **SDK**: `boto3`
- **AWS Region**: `ap-south-1`
- **DynamoDB Table**: `CGIModelResults`
- **Global Secondary Index (GSI)**: `GSI_SN` (Partition Key: `serialNumber`, Sort Key: `dataType`)
- **Handler**: `lambda_function.lambda_handler`

---

## CORS Headers
All HTTP responses include standard CORS headers:
```json
{
  "Content-Type": "application/json",
  "Access-Control-Allow-Origin": "*"
}
```

---

## DynamoDB Data Modeling
- **Partition Key (`PK`)**: `userId`
- **Sort Key (`SK`)**: `{timestamp}#{serialNumber}#{dataType}`
- **Global Secondary Index (`GSI_SN`)**:
  - Partition Key: `serialNumber`
  - Sort Key: `dataType`
- **Attributes**:
  - `serialNumber` (string)
  - `dataType` (string, uppercase)
  - `timestamp` (string)
  - `payload` (map/object)
  - `createdAt` (ISO 8601 UTC timestamp)

---

## API Endpoints & Behavior

### 1. Save Model Output (`POST /getModelOutput`)

Saves a new analysis result item into the `CGIModelResults` table.

#### Request Body Fields (all required):
- `userId` (string): Unique user identifier.
- `serialNumber` (string): Device or sensor serial number.
- `dataType` (string): Model output or data type (e.g., `NDVI`, `SOIL_MOISTURE`). Converted to uppercase.
- `timestamp` (string): ISO/RFC timestamp of the observation.
- `payload` (object): Result payload or model output metrics.

#### Example Request:
```json
{
  "userId": "user123",
  "serialNumber": "SN123456",
  "dataType": "NDVI",
  "timestamp": "2026-10-12T10:30:00Z",
  "payload": {
    "result": "example",
    "score": 0.82
  }
}
```

#### Status Codes & Responses:
- **`200 OK`**: Item saved successfully.
  ```json
  {
    "success": true,
    "message": "Data saved successfully",
    "item": {
      "PK": "user123",
      "SK": "2026-10-12T10:30:00Z#SN123456#NDVI",
      "serialNumber": "SN123456",
      "dataType": "NDVI",
      "timestamp": "2026-10-12T10:30:00Z",
      "payload": {
        "result": "example",
        "score": 0.82
      },
      "createdAt": "2026-10-12T16:00:00.000000Z"
    }
  }
  ```
- **`400 Bad Request`**: Missing required fields.
  ```json
  {
    "success": false,
    "message": "Missing required fields"
  }
  ```
- **`500 Internal Server Error`**: Unexpected error.
  ```json
  {
    "success": false,
    "message": "Internal server error",
    "error": "Error details"
  }
  ```

---

### 2. Fetch Model Output (`GET /getModelOutput`)

Retrieves model results using query parameters.

#### Query Parameters:
- `userId` (string, optional)
- `serialNumber` (string, optional)
- `dataType` (string, optional)
- `date` (string, optional): Prefix string for filtering items by date/timestamp (e.g., `2026-10-12`).

#### Query Modes:
Callers must supply either **`serialNumber` and `dataType` together**, or **`userId`**.

##### Mode A: Query by `serialNumber` and `dataType` (Takes Precedence)
When both `serialNumber` and `dataType` are supplied in the query string:
- Queries GSI `GSI_SN` with `serialNumber = :sn AND dataType = :dt` (with `dataType` converted to uppercase).
- Results are sorted in descending order (`ScanIndexForward=False`).
- If `date` is supplied, returned items are filtered in memory where `timestamp` starts with the `date` string.

**Example Request:**
`GET /getModelOutput?serialNumber=SN123456&dataType=NDVI&date=2026-10-12`

##### Mode B: Query by `userId`
When `serialNumber` and `dataType` are not both supplied, `userId` is required:
- If `date` is provided, queries the primary index using:
  `PK = :pk AND begins_with(SK, :date)`
- If `date` is not provided, queries using:
  `PK = :pk`
- Results are sorted in descending order (`ScanIndexForward=False`).
- If `dataType` is provided, items are filtered in memory where `item.dataType == dataType.upper()`.

**Example Request:**
`GET /getModelOutput?userId=user123&dataType=NDVI`

#### Status Codes & Responses:
- **`200 OK`**: Successful query.
  ```json
  {
    "success": true,
    "count": 1,
    "data": [
      {
        "PK": "user123",
        "SK": "2026-10-12T10:30:00Z#SN123456#NDVI",
        "serialNumber": "SN123456",
        "dataType": "NDVI",
        "timestamp": "2026-10-12T10:30:00Z",
        "payload": {
          "result": "example"
        },
        "createdAt": "2026-10-12T16:00:00.000000Z"
      }
    ]
  }
  ```
- **`400 Bad Request`**: Neither `serialNumber + dataType` nor `userId` was supplied.
  ```json
  {
    "success": false,
    "message": "Either userId OR serialNumber+dataType required"
  }
  ```
- **`500 Internal Server Error`**: Unexpected error.
  ```json
  {
    "success": false,
    "message": "Internal server error",
    "error": "Error details"
  }
  ```

---

### 3. Unsupported HTTP Methods
For any HTTP method other than `GET` or `POST`:
- **`405 Method Not Allowed`**:
  ```json
  {
    "success": false,
    "message": "Method not allowed"
  }
  ```

---

## DynamoDB Serialization
The Lambda includes a custom `DecimalEncoder` that converts `decimal.Decimal` objects from DynamoDB into native integers or floating-point numbers during `json.dumps()`, avoiding JSON serialization errors while preserving accurate data representations.
