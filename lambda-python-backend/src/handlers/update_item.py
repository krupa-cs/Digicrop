from typing import Dict, Any
from utils.logger import get_logger
from utils.response import create_response, error_response
from utils.validation import validate_body
from services import dynamodb_service

logger = get_logger(__name__)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for updating an existing item.
    """
    try:
        logger.info("Received update_item request")
        
        # 1. Extract path parameters
        path_parameters = event.get('pathParameters') or {}
        pk = path_parameters.get('PK')
        sk = path_parameters.get('SK')
        
        if not pk or not sk:
            logger.warning("Missing path parameters (PK or SK)")
            return error_response(400, "Missing path parameters (PK or SK)")
            
        # 2. Extract and validate body
        body_str = event.get('body')
        is_valid, updates, err_msg = validate_body(body_str)
        if not is_valid:
            logger.warning(f"Validation failed: {err_msg}")
            return error_response(400, err_msg)
            
        if not updates:
             return error_response(400, "No updates provided")
             
        # 3. Verify item exists before updating
        existing_item = dynamodb_service.get_item(pk, sk)
        if not existing_item:
            logger.warning(f"Item not found for PK: {pk}, SK: {sk}")
            return error_response(404, "Item not found")
            
        # 4. Perform update
        updated_item = dynamodb_service.update_item(pk, sk, updates)
        
        logger.info(f"Successfully updated item for PK: {pk}, SK: {sk}")
        return create_response(200, {"message": "Item updated successfully", "item": updated_item})
        
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        return error_response(500, "Internal Server Error")
