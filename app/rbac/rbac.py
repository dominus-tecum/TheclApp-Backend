# Role-Based Access Control (RBAC) definitions and utilities

from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    PATIENT = "patient"

def has_role(user, required_role: Role):
    """
    Check if the user has the required role.
    Usage: has_role(current_user, Role.ADMIN)
    """
    return user.role == required_role

def role_required(required_role: Role):
    """
    Decorator to require a specific role for route access.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            if not user or user.role != required_role:
                raise PermissionError("Insufficient privileges")
            return func(*args, **kwargs)
        return wrapper
    return decorator