# app/authentication/models.py

"""
Authentication models.

Reuses the User model defined in app.users.models
to avoid duplicate table definitions.
"""

from app.models import User  # ✅ Import User from users app
