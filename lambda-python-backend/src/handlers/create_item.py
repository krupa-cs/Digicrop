from typing import Dict, Any
from utils.logger import get_logger
from utils.response import create_response, error_response
from utils.validation import validate_body, validate_keys
from services import dynamodb_service

logger = get_logger(__name__)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for creating a new item.
    """
    try:
        logger.info("Received create_item request")
        
        # 1. Extract and validate body
        body_str = event.get('body')
        is_valid, parsed_body, err_msg = validate_body(body_str)
        if not is_valid:
            logger.warning(f"Validation failed: {err_msg}")
            return error_response(400, err_msg)
            
        # 2. Validate required keys (PK, SK)
        keys_valid, key_err = validate_keys(parsed_body)
        if not keys_valid:
            logger.warning(f"Key validation failed: {key_err}")
            return error_response(400, key_err)
            
        pk = parsed_body['PK']
        sk = parsed_body['SK']
        
        # 3. Check if item already exists (optional depending on use case, DynamoDB put_item overwrites by default)
        existing_item = dynamodb_service.get_item(pk, sk)
        if existing_item:
            logger.warning(f"Item already exists for PK: {pk}, SK: {sk}")
            return error_response(409, "Item already exists")
            
        # 4. Insert Item
        dynamodb_service.put_item(parsed_body)
        logger.info(f"Successfully created item for PK: {pk}, SK: {sk}")
        
        return create_response(201, {"message": "Item created successfully", "item": parsed_body})
        
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        return error_response(500, "Internal Server Error")
