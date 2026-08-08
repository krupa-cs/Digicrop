# NDVI Python Lambda API Documentation

This lambda function provides a single API endpoint to retrieve the latest NDVI historical data for a given plot. It queries a DynamoDB table named `ndviHistoricalData`.

## Endpoint Overview

- **Method**: `GET`
- **Description**: Fetches the most recent NDVI data for a specific Partition Key (PK) and Plot ID.

## Request Parameters

The request must include the following query string parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `PK`      | String | Yes | The Partition Key for the query (typically representing a user or organization ID). |
| `PlotId`  | String | Yes | The unique identifier for the specific plot of land. |

### Example Request (via API Gateway)

```http
GET /ndvi?PK=ORG-123&PlotId=P-456
```

## Responses

### Success (200 OK)

Returns the most recent NDVI data record for the plot.

```json
{
  "payload": {
    "PK": "ORG-123",
    "SK": "PD-P-456#20240808",
    "SerialNumber": "DEVICE-001",
    "Date": "2024-08-08T00:00:00Z",
    "CropType": "Wheat",
    "SoilType": "Loam",
    "PlotId": "P-456",
    "PlotLocation": "North Field",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "NDVI": 0.65,
    "polygonPoints": [
      [40.7128, -74.0060],
      [40.7138, -74.0060],
      [40.7138, -74.0070]
    ],
    "totalPixels": 250,
    "pixelNDVIGrid": [ ... ],
    "weather": {
      "temperature": 25,
      "humidity": 60,
      "uvIndex": 8,
      "rainfall": 0,
      "sunrise": "06:15:00",
      "sunset": "20:00:00",
      "maxTemperature": 30,
      "minTemperature": 20,
      "maxHeatIndex": 32,
      "windSpeed": 12.5,
      "windDirection": "NW"
    }
  }
}
```

### Errors

**400 Bad Request**
Returned when required query parameters are missing.
```json
{
  "message": "PK and PlotId are required"
}
```

**404 Not Found**
Returned when no data exists for the given `PK` and `PlotId`.
```json
{
  "message": "No NDVI data found for this plot"
}
```

**500 Internal Server Error**
Returned during an unexpected exception or database connection failure.
```json
{
  "message": "Internal server error",
  "error": "Detailed error message string"
}
```

## Database Details

- **Table**: `ndviHistoricalData`
- **Query Logic**: 
  - `PK = :pk`
  - `SK begins_with "PD-{PlotId}"`
  - `ScanIndexForward = False` (retrieves the newest item first)
  - `Limit = 1` (fetches only the single most recent record)
