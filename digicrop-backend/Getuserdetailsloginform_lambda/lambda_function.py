import logging
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)


cognito = boto3.client(
    "cognito-idp",
    region_name="us-east-1"
)


USER_POOL_ID = "us-east-1_oQejFpiPh"


def lambda_handler(event, context):

    username = event["username"]

    params = {
        "UserPoolId": USER_POOL_ID,
        "Username": username,
    }

    try:

        user_data = cognito.admin_get_user(
            **params
        )

        user_attributes = user_data.get(
            "UserAttributes",
            []
        )

        logger.info(
            "User attributes: %s",
            user_attributes
        )

        return {
            "statusCode": 200,
            "body": user_attributes
        }

    except Exception as error:

        logger.exception(
            "Error retrieving user attributes: %s",
            error
        )

        return {
            "statusCode": 500,
            "body": "Internal Server Error"
        }
