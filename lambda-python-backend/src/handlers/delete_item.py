from typing import Dict, Any
from utils.logger import get_logger
from utils.response import create_response, error_response
from services import dynamodb_service

logger = get_logger(__name__)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for deleting a single item.
    """
    try:
        logger.info("Received delete_item request")
        
        # 1. Extract path parameters
        path_parameters = event.get('pathParameters') or {}
        pk = path_parameters.get('PK')
        sk = path_parameters.get('SK')
        
        if not pk or not sk:
            logger.warning("Missing path parameters (PK or SK)")
            return error_response(400, "Missing path parameters (PK or SK)")
            
        # 2. Verify item exists before deleting (optional, depends on semantics)
        existing_item = dynamodb_service.get_item(pk, sk)
        if not existing_item:
            logger.warning(f"Item not found for PK: {pk}, SK: {sk}")
            return error_response(404, "Item not found")
            
        # 3. Delete Item
        dynamodb_service.delete_item(pk, sk)
        
        logger.info(f"Successfully deleted item for PK: {pk}, SK: {sk}")
        return create_response(200, {"message": "Item deleted successfully"})
        
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        return error_response(500, "Internal Server Error")
