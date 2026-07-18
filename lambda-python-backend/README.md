# AWS Lambda Backend: Node.js to Python Migration

This project represents the complete migration of an AWS Lambda serverless backend from Node.js to Python 3.12. It utilizes `boto3` to perform CRUD operations on Amazon DynamoDB.

## 🚀 Key Migration Improvements & Differences
- **Python 3.12 Runtime**: Upgraded from Node.js (16/18/20) to a fast and fully-supported Python environment.
- **Execution Context Reuse**: `boto3` resources (TCP connections) are initialized globally (outside the handler) to reduce warm-start latency—a critical AWS Lambda best practice.
- **Strict Validation**: Input payloads are strongly validated via custom utility functions.
- **Structured Logging**: Uses Python's native `logging` module to output standardized format for AWS CloudWatch rather than scattered `console.log()` calls.
- **Modular Architecture**: Handlers, services (DynamoDB abstraction), and utilities (logging, responses, validation) are neatly separated into individual folders inside `src/`.
- **Infrastructure as Code (SAM)**: Uses AWS Serverless Application Model (`template.yaml`) for clean and repeatable deployments.

## 📁 Project Structure

```text
├── src/
│   ├── handlers/
│   │   ├── create_item.py    # (POST) Creates new items
│   │   ├── get_item.py       # (GET) Fetches a single item by PK and SK
│   │   ├── update_item.py    # (PUT) Updates existing attributes
│   │   └── delete_item.py    # (DELETE) Deletes an item
│   ├── services/
│   │   └── dynamodb_service.py # Abstracted boto3 logic 
│   ├── utils/
│   │   ├── logger.py         # Structured logging configuration
│   │   ├── response.py       # Standardized API Gateway responses
│   │   └── validation.py     # Body parsing and PK/SK checks
├── template.yaml             # SAM Deployment Template
└── requirements.txt          # Python dependencies
```

## 🛠️ Deployment Instructions

You will need the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) installed.

1. **Build the Application**:
   SAM will package the Python code and install the dependencies from `requirements.txt`.
   ```bash
   sam build
   ```

2. **Deploy the Application**:
   Use guided deployment to configure your stack name and AWS Region.
   ```bash
   sam deploy --guided
   ```

## 📝 Example Requests & Responses

### 1. Create Item (POST `/items`)
**Request:**
```bash
curl -X POST https://api-id.execute-api.region.amazonaws.com/Prod/items \
  -H "Content-Type: application/json" \
  -d '{"PK": "USER#123", "SK": "PROFILE", "name": "John Doe", "email": "john@example.com"}'
```
**Response (201 Created):**
```json
{
  "message": "Item created successfully",
  "item": {
    "PK": "USER#123",
    "SK": "PROFILE",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### 2. Get Item (GET `/items/USER#123/PROFILE`)
**Request:**
```bash
curl https://api-id.execute-api.region.amazonaws.com/Prod/items/USER%23123/PROFILE
```
**Response (200 OK):**
```json
{
  "PK": "USER#123",
  "SK": "PROFILE",
  "name": "John Doe",
  "email": "john@example.com"
}
```

### 3. Update Item (PUT `/items/USER#123/PROFILE`)
**Request:**
```bash
curl -X PUT https://api-id.execute-api.region.amazonaws.com/Prod/items/USER%23123/PROFILE \
  -H "Content-Type: application/json" \
  -d '{"name": "Johnny Doe"}'
```
**Response (200 OK):**
```json
{
  "message": "Item updated successfully",
  "item": {
    "PK": "USER#123",
    "SK": "PROFILE",
    "name": "Johnny Doe",
    "email": "john@example.com"
  }
}
```

## 💡 Recommendations for Maintenance
1. **Pydantic**: As your data models grow more complex, consider replacing `utils.validation.py` with Pydantic models for strict type checking.
2. **Lambda Powertools**: For advanced production needs, swap standard logging with [AWS Lambda Powertools for Python](https://awslabs.github.io/aws-lambda-powertools-python/latest/) which includes optimized tracers, metrics, and loggers natively.
