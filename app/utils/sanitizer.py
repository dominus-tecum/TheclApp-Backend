import re
from bleach import clean

def sanitize_string(value: str) -> str:
    """Remove HTML/script tags from string"""
    if not value or not isinstance(value, str):
        return value
    
    # Remove HTML tags
    cleaned = clean(value, tags=[], attributes={}, strip=True)
    
    # Remove any remaining < and > characters
    cleaned = re.sub(r'<[^>]*>', '', cleaned)
    
    return cleaned.strip()

def sanitize_dict(data: dict) -> dict:
    """Recursively sanitize all string values in a dictionary"""
    if not data:
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(item) if isinstance(item, str) else 
                sanitize_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        else:
            sanitized[key] = value
    return sanitized