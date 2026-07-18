import json
from typing import Any, Dict

def create_response(status_code: int, body: Any = None) -> Dict[str, Any]:
    """
    Generates a standard API Gateway proxy response.
    """
    response: Dict[str, Any] = {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*" # Required for CORS support to work with Serverless REST API
        }
    }
    
    if body is not None:
        response["body"] = json.dumps(body)
        
    return response

def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Generates a standardized error response.
    """
    return create_response(status_code, {"error": message})
