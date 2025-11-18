# RBAC roles and permissions (example structure)

ROLES = {
    "admin": {
        "permissions": [
            "view_users",
            "edit_users",
            "delete_users",
            "view_records",
            "edit_records",
            "delete_records",
            "manage_settings",
        ]
    },
    "doctor": {
        "permissions": [
            "view_users",
            "view_records",
            "edit_records"
        ]
    },
    "nurse": {
        "permissions": [
            "view_users",
            "view_records"
        ]
    },
    "patient": {
        "permissions": [
            "view_own_record"
        ]
    },
}

def has_permission(role, permission):
    return permission in ROLES.get(role, {}).get("permissions", [])