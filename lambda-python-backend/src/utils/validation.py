from typing import Dict, Any, Tuple
import json

def validate_body(body: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Validates and parses JSON body string.
    Returns (is_valid, parsed_body, error_message).
    """
    if not body:
        return False, {}, "Missing request body"
        
    try:
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            return False, {}, "Request body must be a JSON object"
        return True, parsed, ""
    except json.JSONDecodeError:
        return False, {}, "Invalid JSON format"

def validate_keys(item: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates presence of PK and SK.
    """
    if "PK" not in item:
        return False, "Missing 'PK' (Partition Key)"
    if "SK" not in item:
        return False, "Missing 'SK' (Sort Key)"
    return True, ""
