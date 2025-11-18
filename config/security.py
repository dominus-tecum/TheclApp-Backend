# Security policy configuration example

SECURITY_SETTINGS = {
    "password_min_length": 12,
    "password_complexity": True,
    "require_2fa": True,
    "session_timeout_minutes": 15,
    "enforce_https": True,
    "jwt_expiry_minutes": 60,
    "allowed_login_attempts": 5,
    "lockout_duration_minutes": 30,
}