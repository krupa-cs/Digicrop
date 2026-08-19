# Blob Data Lambda

## 1. Lambda Purpose
Saves plot details to DynamoDB, handling incoming crop, location, and farm data.

## 2. Node.js → Python Migration
This Lambda function has been successfully migrated from Node.js to Python. It uses `boto3` for AWS interactions and standard Python `uuid` instead of `aws-sdk`. 

## 3. AWS Service Used
- AWS Lambda
- Amazon DynamoDB

## 4. DynamoDB Table
`MainTransactionData`

## 5. Input Fields
- `userId` (String)
- `date` (String)
- `name` (String)
- `latitude` (Number)
- `longitude` (Number)
- `cropType` (String)
- `variety` (String, Optional)
- `serialNumber` (String)
- `soilType` (String)
- `plotLocation` (String)
- `polygonPoints` (Array, Optional)
- `root_depth` (Number)
- `Irrigation_efficiency` (Number)
- `target_yield_t_acre` (Number)
- `fertilizer_application_method` (String)
- `area_of_field_acre` (Number)
- `age_years` (Number)
- `plant_density_per_acre` (Number)

## 6. Required Fields
`userId`, `date`, `name`, `latitude`, `longitude`, `cropType`, `serialNumber`, `soilType`, `plotLocation`, `root_depth`, `Irrigation_efficiency`, `target_yield_t_acre`, `fertilizer_application_method`, `area_of_field_acre`, `age_years`, `plant_density_per_acre`.

## 7. polygonPoints Default Behavior
If `polygonPoints` is omitted, it defaults to an empty array `[]`.

## 8. DynamoDB Item Structure
```json
{
    "PK": "userId",
    "SK": "PD-<uuid>",
    "PlotId": "<uuid>",
    "type": "Plot Details",
    "Date": "date",
    "Name": "name",
    "latitude": "latitude",
    "longitude": "longitude",
    "CropType": "cropType",
    "Variety": "variety",
    "SerialNumber": "serialNumber",
    "SoilType": "soilType",
    "PlotLocation": "plotLocation",
    "root_depth": "root_depth",
    "Irrigation_efficiency": "Irrigation_efficiency",
    "target_yield_t_acre": "target_yield_t_acre",
    "fertilizer_application_method": "fertilizer_application_method",
    "area_of_field_acre": "area_of_field_acre",
    "age_years": "age_years",
    "plant_density_per_acre": "plant_density_per_acre",
    "polygonPoints": "polygonPoints"
}
```

## 9. Response Codes
- **200 OK**: Request processed, plot details saved successfully.
- **400 Bad Request**: Missing required fields.
- **500 Internal Server Error**: Internal lambda processing error (e.g., DynamoDB errors).

## 10. Example Request
```json
{
    "userId": "user-123",
    "date": "2023-10-01",
    "name": "Plot 1",
    "latitude": 12.34,
    "longitude": 56.78,
    "cropType": "Wheat",
    "variety": "Durum",
    "serialNumber": "SN-001",
    "soilType": "Loamy",
    "plotLocation": "North Field",
    "polygonPoints": [{"lat": 12.34, "lng": 56.78}],
    "root_depth": 0.5,
    "Irrigation_efficiency": 0.8,
    "target_yield_t_acre": 2.0,
    "fertilizer_application_method": "Broadcast",
    "area_of_field_acre": 10,
    "age_years": 1,
    "plant_density_per_acre": 4000
}
```

## 11. Example Responses
**Success (200)**:
```json
{
    "message": "Plot saved successfully",
    "plotId": "abc-1234-defg-5678"
}
```

**Validation Error (400)**:
```json
{
    "message": "Missing required fields"
}
```

**Server Error (500)**:
```json
{
    "error": "Error message from DynamoDB/boto3"
}
```

## 12. OpenAPI Documentation Location
OpenAPI Specification: `api/openapi.yaml`
