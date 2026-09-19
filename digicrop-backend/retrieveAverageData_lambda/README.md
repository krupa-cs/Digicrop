# retrieveAverageData Lambda

## Overview

The `retrieveAverageData` Lambda retrieves data from the `RawData` DynamoDB table based on a SerialNumber and date range.

The query behavior depends on the requested date range.

For ranges shorter than 20 days, the Lambda queries the normal RawData sort-key range.

For ranges of 20 days or more, the Lambda queries records using the `DialyAverage-` sort-key prefix.

## Runtime

Python

## AWS Service

Amazon DynamoDB

## Region

us-east-1

## DynamoDB Table

RawData

## Handler

lambda_handler(event, context)

## Input

The Lambda expects:

- SerialNumber
- startDate
- endDate

Example:

```json
{
  "SerialNumber": "SN001",
  "startDate": "2026-08-01",
  "endDate": "2026-08-10"
}
```

## Query Behavior

### Less than 20 days

The Lambda queries:

PK = SerialNumber
SK BETWEEN startDate AND endDate

The start date is set to the beginning of the day.

The end date is set to the end of the day.

### 20 days or more

The Lambda queries:

PK = SerialNumber
SK BETWEEN DialyAverage-startDate AND DialyAverage-endDate

The spelling DialyAverage- is intentionally preserved from the original Lambda.

## Response

The successful response preserves the original structure:

```json
{
  "body": []
}
```

The body contains the DynamoDB query items.

## Migration

This Lambda was migrated from Node.js AWS SDK DocumentClient to Python boto3 while preserving the original DynamoDB table, region, query logic, date-range behavior, and response structure.
