# Get Timeseries Data Lambda

## Overview

This Lambda retrieves historical NDVI and weather time-series data for a plot between a specified start date and end date.

The returned data is suitable for graph/time-series visualization.

## Runtime

Python

## AWS Service

Amazon DynamoDB

## Region

us-east-1

## DynamoDB Table

ndviHistoricalData

## HTTP Method

GET

## Query Parameters

The Lambda requires:

- PK
- PlotId
- startDate
- endDate

Example:

GET /data?PK=USER123&PlotId=PLOT001&startDate=2026-01-01&endDate=2026-01-31

## DynamoDB Query

The Lambda constructs:

PD-{PlotId}-{startDate}

and

PD-{PlotId}-{endDate}

and queries:

PK = :pk AND SK BETWEEN :start AND :end

Results are returned in ascending sort-key order.

Therefore the time-series data is returned from oldest to latest.

## Response

Successful response:

```json
{
  "count": 2,
  "startDate": "2026-01-01",
  "endDate": "2026-01-31",
  "data": [
    {
      "date": "2026-01-01",
      "plotId": "PLOT001",
      "plotName": "Demo Plot",
      "cropType": "Rice",
      "soilType": "Clay",
      "plotLocation": "Bangalore",
      "latitude": 12.9716,
      "longitude": 77.5946,
      "ndvi": 0.72
    }
  ]
}
```
