# Getuserdetailsloginform Lambda

## Overview

This Lambda retrieves user details from an Amazon Cognito User Pool using the username provided in the Lambda event.

## Runtime

- Python
- boto3

## AWS Service

Amazon Cognito Identity Provider

## Cognito User Pool

User Pool ID:

us-east-1_oQejFpiPh

## Handler

lambda_function.lambda_handler

## Input

The Lambda expects:

```json
{
  "username": "example-username"
}
```

## Behavior

The Lambda:

1. Reads `username` from the event.
2. Calls Cognito `AdminGetUser`.
3. Retrieves the user's `UserAttributes`.
4. Returns the attributes with statusCode 200.
5. Returns statusCode 500 with `Internal Server Error` if an exception occurs.

## Migration

This Lambda was migrated from Node.js AWS SDK to Python boto3 while preserving the existing Cognito functionality and response behavior.
