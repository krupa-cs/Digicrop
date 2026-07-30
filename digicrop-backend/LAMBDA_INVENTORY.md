# AWS Lambda Inventory

This document tracks all AWS Lambda functions within the repository and their migration status to Python.

| Lambda name | HTTP method | API endpoint | Purpose | DynamoDB table(s) | PK / SK | Request parameters | Dependencies | Migrated to Python |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `telemetry_lambda` | GET | *N/A (Requires API Gateway Mapping)* | Retrieve device telemetry data (either the latest record or within a specified date range). | `TelemetryData` | **PK:** `SerialNumber`<br>**SK:** `SK` (Timestamp) | **Query Strings:**<br>- `SerialNumber` (Required)<br>- `startDate` (Optional)<br>- `endDate` (Optional) | `boto3` | **Yes** |
