import json
import logging
from decimal import Decimal

import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)


dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1"
)

table = dynamodb.Table("ndviHistoricalData")


class DecimalEncoder(json.JSONEncoder):
    """
    Convert DynamoDB Decimal values into JSON-compatible numbers.
    """

    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)

        return super().default(obj)


def response(status_code, body):
    """
    Create an API Gateway-compatible response.
    """

    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(
            body,
            cls=DecimalEncoder
        ),
    }


def get_nested_value(data, *keys, default=None):
    """
    Safely retrieve nested dictionary values.

    This is used to preserve the Node.js optional-chaining
    and nullish fallback behavior.
    """

    current = data

    for key in keys:
        if not isinstance(current, dict):
            return default

        current = current.get(key)

        if current is None:
            return default

    return current


def lambda_handler(event, context):
    try:
        logger.info("Incoming event: %s", json.dumps(event, default=str))

        query_params = event.get("queryStringParameters") or {}

        PK = query_params.get("PK")
        PlotId = query_params.get("PlotId")
        startDate = query_params.get("startDate")
        endDate = query_params.get("endDate")

        # Preserve original validation behavior
        if not PK or not PlotId or not startDate or not endDate:
            return response(
                400,
                {
                    "message": "PK, PlotId, startDate, endDate are required"
                }
            )

        # Preserve original SK construction
        sk_start = f"PD-{PlotId}-{startDate}"
        sk_end = f"PD-{PlotId}-{endDate}"

        # Preserve original DynamoDB query
        result = table.query(
            KeyConditionExpression="PK = :pk AND SK BETWEEN :start AND :end",
            ExpressionAttributeValues={
                ":pk": PK,
                ":start": sk_start,
                ":end": sk_end,
            },
            ScanIndexForward=True,
        )

        items = result.get("Items", [])

        history = []

        for item in items:

            forecast_days = get_nested_value(
                item,
                "weather",
                "raw",
                "forecastDays",
                default=[]
            )

            if isinstance(forecast_days, list) and len(forecast_days) > 0:
                forecast = forecast_days[0] or {}
            else:
                forecast = {}

            daytime = forecast.get(
                "daytimeForecast",
                {}
            ) or {}

            history_item = {
                # Plot Details
                "date": item.get("Date"),
                "plotId": item.get("PlotId"),
                "plotName": item.get("Name"),
                "cropType": item.get("CropType"),
                "soilType": item.get("SoilType"),
                "plotLocation": item.get("PlotLocation"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),

                # NDVI
                "ndvi": item.get("polygonAverageNDVI"),

                # Current Weather
                "temperature": get_nested_value(
                    item, "weather", "temperature"
                ),
                "humidity": get_nested_value(
                    item, "weather", "humidity"
                ),
                "rainfall": get_nested_value(
                    item, "weather", "rainfall"
                ),
                "uvIndex": get_nested_value(
                    item, "weather", "uvIndex"
                ),

                # Temperature Metrics
                "maxTemperature": get_nested_value(
                    forecast, "maxTemperature", "degrees"
                ),
                "minTemperature": get_nested_value(
                    forecast, "minTemperature", "degrees"
                ),
                "feelsLikeMax": get_nested_value(
                    forecast, "feelsLikeMaxTemperature", "degrees"
                ),
                "feelsLikeMin": get_nested_value(
                    forecast, "feelsLikeMinTemperature", "degrees"
                ),
                "heatIndex": get_nested_value(
                    forecast, "maxHeatIndex", "degrees"
                ),

                # Wind
                "windSpeed": get_nested_value(
                    daytime, "wind", "speed", "value"
                ),
                "windSpeedUnit": get_nested_value(
                    daytime, "wind", "speed", "unit"
                ),
                "windGust": get_nested_value(
                    daytime, "wind", "gust", "value"
                ),
                "windGustUnit": get_nested_value(
                    daytime, "wind", "gust", "unit"
                ),
                "windDirection": get_nested_value(
                    daytime, "wind", "direction", "cardinal"
                ),
                "windDirectionDegrees": get_nested_value(
                    daytime, "wind", "direction", "degrees"
                ),

                # Clouds
                "cloudCover": daytime.get(
                    "cloudCover"
                ),

                # Rain / Precipitation
                "rainProbability": get_nested_value(
                    daytime,
                    "precipitation",
                    "probability",
                    "percent"
                ),
                "precipitationType": get_nested_value(
                    daytime,
                    "precipitation",
                    "probability",
                    "type"
                ),
                "rainfallForecast": get_nested_value(
                    daytime,
                    "precipitation",
                    "qpf",
                    "quantity"
                ),
                "rainfallUnit": get_nested_value(
                    daytime,
                    "precipitation",
                    "qpf",
                    "unit"
                ),

                # Storms
                "thunderstormProbability": daytime.get(
                    "thunderstormProbability"
                ),

                # Weather Description
                "weatherCondition": get_nested_value(
                    daytime,
                    "weatherCondition",
                    "description",
                    "text"
                ),
                "weatherType": get_nested_value(
                    daytime,
                    "weatherCondition",
                    "type"
                ),

                # Relative Humidity Forecast
                "forecastHumidity": daytime.get(
                    "relativeHumidity"
                ),

                # Sun Events
                "sunrise": get_nested_value(
                    forecast,
                    "sunEvents",
                    "sunriseTime"
                ),
                "sunset": get_nested_value(
                    forecast,
                    "sunEvents",
                    "sunsetTime"
                ),

                # Moon Events
                "moonPhase": get_nested_value(
                    forecast,
                    "moonEvents",
                    "moonPhase"
                ),
                "moonrise": get_nested_value(
                    forecast,
                    "moonEvents",
                    "moonriseTimes",
                    default=[None]
                )[0]
                if isinstance(
                    get_nested_value(
                        forecast,
                        "moonEvents",
                        "moonriseTimes",
                        default=[]
                    ),
                    list
                )
                and len(
                    get_nested_value(
                        forecast,
                        "moonEvents",
                        "moonriseTimes",
                        default=[]
                    )
                ) > 0
                else None,

                "moonset": get_nested_value(
                    forecast,
                    "moonEvents",
                    "moonsetTimes",
                    default=[None]
                )[0]
                if isinstance(
                    get_nested_value(
                        forecast,
                        "moonEvents",
                        "moonsetTimes",
                        default=[]
                    ),
                    list
                )
                and len(
                    get_nested_value(
                        forecast,
                        "moonEvents",
                        "moonsetTimes",
                        default=[]
                    )
                ) > 0
                else None,

                # Timezone
                "timezone": get_nested_value(
                    item,
                    "weather",
                    "raw",
                    "timeZone",
                    "id"
                ),
            }

            history.append(history_item)

        return response(
            200,
            {
                "count": len(history),
                "startDate": startDate,
                "endDate": endDate,
                "data": history,
            }
        )

    except Exception as err:
        logger.exception("NDVI history error")

        return response(
            500,
            {
                "message": "Server error",
                "error": str(err),
            }
        )
