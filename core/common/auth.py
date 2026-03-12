from flask_jwt_extended import get_jwt_identity
from functools import wraps
import jwt
import json

from flask import request
from datetime import datetime, timezone, timedelta
from .db import get_db
from core.config import Config
from .responses import forbidden, http_error
from core.models.roles.repository import user_has_permission

ROUTE_PERMISSIONS = {
    "create_product": "create_product",
    "delete_product": "delete_product",
    "read_product": "read_product",
}

def view_require_permission():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if is_admin():
                return f(*args, **kwargs)

            required_perm = request.args.get("permission")
            if not required_perm:
                return http_error("Permissão não informada", 403)

            user = get_identity()
            if not user_has_permission(get_db(), user["username"], required_perm):
                return http_error("Acesso negado", 403)

            return f(*args, **kwargs)
        return wrapper
    return decorator


def get_identity():
    return json.loads(get_jwt_identity())

def is_admin():
    username = get_identity()["username"]
    with get_db() as db:
        cursor = db.execute("SELECT isAdmin FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
    return bool(row[0])

def require_permission(permission_name=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if is_admin():
                return f(*args, **kwargs)

            if permission_name is None:
                return forbidden()

            user = get_identity()
            if not user_has_permission(get_db(), user["username"], permission_name):
                return forbidden()
            return f(*args, **kwargs)
        return wrapper
    return decorator

def create_profile_token(username, user_id, is_admin):
    payload = {
        "sub": username,
        "id": user_id,
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, Config.PROFILE_SECRET, algorithm="HS256")
    return token
