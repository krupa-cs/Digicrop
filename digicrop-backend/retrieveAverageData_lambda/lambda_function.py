import json
import logging
from datetime import datetime, timezone
from decimal import Decimal

import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)


dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1"
)

table = dynamodb.Table("RawData")


FIVE_HOURS_THIRTY_MINUTES_MS = (
    5 * 60 * 60 * 1000
    + 30 * 60 * 1000
)


class DecimalEncoder(json.JSONEncoder):
    """
    Converts DynamoDB Decimal values into
    JSON-compatible numbers.
    """

    def default(self, obj):

        if isinstance(obj, Decimal):

            if obj % 1 == 0:
                return int(obj)

            return float(obj)

        return super().default(obj)


def parse_date(date_string):
    """
    Parse date values supplied by the Lambda event.
    """

    if not date_string:
        raise ValueError("Date value is required")

    value = str(date_string).strip()

    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    try:
        return datetime.fromisoformat(value)

    except ValueError:

        for fmt in (
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
        ):

            try:
                return datetime.strptime(
                    value,
                    fmt
                )

            except ValueError:
                continue

    raise ValueError(
        f"Invalid date format: {date_string}"
    )


def get_diff_days(start_date, end_date):

    date1 = parse_date(start_date)
    date2 = parse_date(end_date)

    difference_ms = (
        date2 - date1
    ).total_seconds() * 1000

    return int(
        difference_ms /
        (1000 * 60 * 60 * 24)
    )


def get_unix_seconds(
    date_string,
    end_of_day=False
):
    """
    Convert the supplied date into Unix seconds.

    Start date:
    00:00:00

    End date:
    23:59:59.999
    """

    dt = parse_date(date_string)

    if end_of_day:

        dt = dt.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999000
        )

    else:

        dt = dt.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    if dt.tzinfo is None:

        dt = dt.replace(
            tzinfo=timezone.utc
        )

    return dt.timestamp()


def read_message(event):

    serial_number = event.get(
        "SerialNumber"
    )

    start_date_input = event.get(
        "startDate"
    )

    end_date_input = event.get(
        "endDate"
    )

    diff_days = get_diff_days(
        start_date_input,
        end_date_input
    )

    start_date = get_unix_seconds(
        start_date_input,
        end_of_day=False
    )

    end_date = get_unix_seconds(
        end_date_input,
        end_of_day=True
    )

    if diff_days < 20:

        params = {

            "KeyConditionExpression":
                "PK=:s AND SK BETWEEN :start AND :end",

            "ExpressionAttributeValues": {

                ":s": serial_number,

                ":start":
                    str(start_date),

                ":end":
                    str(end_date),

            },
        }

    else:

        params = {

            "KeyConditionExpression":
                "PK=:s AND SK BETWEEN :start AND :end",

            "ExpressionAttributeValues": {

                ":s": serial_number,

                ":start":
                    f"DialyAverage-{start_date}",

                ":end":
                    f"DialyAverage-{end_date}",

            },
        }

    logger.info(
        "retrieveAverageData DynamoDB query: %s",
        params
    )

    return table.query(
        **params
    )


def lambda_handler(event, context):

    try:

        logger.info(
            "Incoming event: %s",
            json.dumps(
                event,
                default=str
            )
        )

        result = read_message(event)

        items = result.get(
            "Items",
            []
        )

        return {
            "body": json.dumps(
                items,
                cls=DecimalEncoder
            )
        }

    except Exception as error:

        logger.exception(
            "retrieveAverageData error"
        )

        return {
            "body": json.dumps(
                {
                    "error": str(error)
                }
            )
        }
