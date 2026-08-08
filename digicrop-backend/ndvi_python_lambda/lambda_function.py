import json
import logging
import boto3
from decimal import Decimal
from typing import Any, Dict, List, Optional
from boto3.dynamodb.conditions import Key

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS resources globally to allow connection reuse across invocations
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("ndviHistoricalData")

def safe_get(data: dict, *keys: str) -> Any:
    """
    Safely retrieves a nested value from a dictionary, returning None if
    any key in the path does not exist. This replicates JavaScript's
    optional chaining (?.).
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and len(current) > key:
            current = current[key]
        else:
            return None
    return current

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert to int if it has no fractional part, else float
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def build_response(status_code: int, body_data: dict) -> dict:
    """
    Constructs the HTTP response required by API Gateway.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(body_data, cls=DecimalEncoder)
    }

def build_weather(item: dict) -> dict:
    """
    Extracts and formats weather data from the DynamoDB item.
    """
    weather_node = safe_get(item, "weather") or {}
    
    return {
        "temperature": safe_get(weather_node, "temperature"),
        "humidity": safe_get(weather_node, "humidity"),
        "uvIndex": safe_get(weather_node, "uvIndex"),
        "rainfall": safe_get(weather_node, "rainfall"),
        "sunrise": safe_get(weather_node, "raw", "forecastDays", 0, "sunEvents", "sunriseTime"),
        "sunset": safe_get(weather_node, "raw", "forecastDays", 0, "sunEvents", "sunsetTime"),
        "maxTemperature": safe_get(weather_node, "raw", "forecastDays", 0, "maxTemperature", "degrees"),
        "minTemperature": safe_get(weather_node, "raw", "forecastDays", 0, "minTemperature", "degrees"),
        "maxHeatIndex": safe_get(weather_node, "raw", "forecastDays", 0, "maxHeatIndex", "degrees"),
        "windSpeed": safe_get(weather_node, "raw", "forecastDays", 0, "daytimeForecast", "wind", "speed", "value"),
        "windDirection": safe_get(weather_node, "raw", "forecastDays", 0, "daytimeForecast", "wind", "direction", "cardinal")
    }

def build_payload(item: dict) -> dict:
    """
    Constructs the payload structure based on the fetched item.
    """
    # Use .get() for top-level keys to safely return None if missing,
    # replicating JS behavior for missing properties (`item.Date`, etc.)
    return {
        "PK": item.get("PK"),
        "SK": item.get("SK"),
        "SerialNumber": item.get("SerialNumber"),
        "Date": item.get("Date"),
        "CropType": item.get("CropType"),
        "SoilType": item.get("SoilType"),
        "PlotId": item.get("PlotId"),
        "PlotLocation": item.get("PlotLocation"),
        "latitude": item.get("latitude"),
        "longitude": item.get("longitude"),
        
        "NDVI": item.get("polygonAverageNDVI"),
        
        "polygonPoints": item.get("polygonPoints", []),
        
        "totalPixels": item.get("totalPixels", 0),
        "pixelNDVIGrid": item.get("pixelNDVIGrid", []),
        
        "weather": build_weather(item)
    }

def handler(event: dict, context: Any) -> dict:
    """
    AWS Lambda entry point.
    """
    try:
        query_params = event.get("queryStringParameters") or {}
        pk = query_params.get("PK")
        plot_id = query_params.get("PlotId")

        # -----------------------------
        # 1️⃣ Validate input
        # -----------------------------
        if not pk or not plot_id:
            return build_response(400, {"message": "PK and PlotId are required"})

        # -----------------------------
        # 2️⃣ Query MAIN TABLE (NOT GSI)
        # -----------------------------
        # Boto3 syntax for query condition: PK = :pk AND begins_with(SK, :prefix)
        prefix = f"PD-{plot_id}"
        
        response = table.query(
            KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with(prefix),
            ScanIndexForward=False,  # newest first
            Limit=1
        )

        items = response.get("Items", [])
        
        if not items:
            return build_response(404, {"message": "No NDVI data found for this plot"})

        item = items[0]

        logger.info(f"Returned Date: {item.get('Date')}")
        
        # Determine pixelNDVIGrid length safely
        pixel_grid = item.get("pixelNDVIGrid")
        pixel_count = len(pixel_grid) if isinstance(pixel_grid, list) else None
        logger.info(f"Pixel Count: {pixel_count}")

        # -----------------------------
        # 3️⃣ Build Payload
        # -----------------------------
        payload = build_payload(item)

        # -----------------------------
        # 4️⃣ Success Response
        # -----------------------------
        return build_response(200, {"payload": payload})

    except Exception as e:
        logger.error(f"Lambda NDVI Error: {e}", exc_info=True)
        return build_response(500, {
            "message": "Internal server error",
            "error": str(e)
        })
