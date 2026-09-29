# tokenToDB Lambda

## Overview
This Lambda stores or updates an Expo push notification token in the MainTransactionData DynamoDB table.

## Runtime
- Python
- boto3

## DynamoDB
- Table: MainTransactionData
- Key structure:
  - PK = userID
  - Existing token records use SK beginning with `ExpoToken`
  - New records use `ExpoToken-{UUID}`

## Input

The Lambda expects:

```json
{
  "userID": "user-id",
  "tokenId": "expo-token"
}
```

## Behavior

1. Query MainTransactionData for an existing item where:
   - PK = userID
   - SK begins with `ExpoToken`

2. If found:
   - Update the `Token` attribute.
   - Return statusCode 200 with the updated attributes.

3. If not found:
   - Create a new item with:
     - PK
     - ExpoToken-{UUID} as SK
     - Token
   - Return statusCode 200 with:
     `Successfully created Item`

4. If an error occurs:
   - Return statusCode 500 with:
     `Error updating or creating item`

## Migration Notes

This is a Node.js-to-Python migration using boto3. The original DynamoDB behavior and response behavior have been preserved.
