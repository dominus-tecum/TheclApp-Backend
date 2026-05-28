import secrets

def generate_patient_token() -> str:
    """Generate a secure, unique patient token"""
    return f"pat_{secrets.token_urlsafe(16)}"