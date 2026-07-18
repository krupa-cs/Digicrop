import os
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize outside handler for execution context reuse (Connection pooling)
TABLE_NAME = os.environ.get("TABLE_NAME")
if TABLE_NAME:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
else:
    dynamodb = None
    table = None

def get_item(pk: str, sk: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a single item by PK and SK.
    """
    try:
        response = table.get_item(
            Key={
                'PK': pk,
                'SK': sk
            }
        )
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error fetching item: {e}")
        raise e

def put_item(item: Dict[str, Any]) -> None:
    """
    Inserts or overwrites an item.
    """
    try:
        table.put_item(Item=item)
    except ClientError as e:
        logger.error(f"Error putting item: {e}")
        raise e

def update_item(pk: str, sk: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Dynamically updates attributes of an existing item.
    """
    if not updates:
        return None
        
    update_expr = "SET "
    expr_attr_values = {}
    expr_attr_names = {}
    
    # We must not update the keys
    safe_updates = {k: v for k, v in updates.items() if k not in ['PK', 'SK']}
    if not safe_updates:
         return get_item(pk, sk)

    for i, (k, v) in enumerate(safe_updates.items()):
        attr_key = f"#attr{i}"
        val_key = f":val{i}"
        update_expr += f"{attr_key} = {val_key}, "
        expr_attr_names[attr_key] = k
        expr_attr_values[val_key] = v

    update_expr = update_expr.rstrip(", ")

    try:
        response = table.update_item(
            Key={'PK': pk, 'SK': sk},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="ALL_NEW"
        )
        return response.get('Attributes')
    except ClientError as e:
        logger.error(f"Error updating item: {e}")
        raise e

def delete_item(pk: str, sk: str) -> None:
    """
    Deletes an item by PK and SK.
    """
    try:
        table.delete_item(
            Key={
                'PK': pk,
                'SK': sk
            }
        )
    except ClientError as e:
        logger.error(f"Error deleting item: {e}")
        raise e
